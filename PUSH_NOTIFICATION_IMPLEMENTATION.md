# Push Notification Implementation Guide
## Expense Added by Friend - Feature Implementation

## Overview

This document outlines the recommended approach for implementing push notifications when a friend adds an expense in the expense tracker application. The notification should alert users in real-time when their friend creates a new expense entry.

---

## 1. Push Notification Service Options

### Option A: Firebase Cloud Messaging (FCM) - **RECOMMENDED**
**Best for:** Cross-platform support (Web, iOS, Android)

**Pros:**
- Free tier with generous limits
- Works on web, iOS, and Android
- Reliable delivery
- Easy to integrate
- Built-in analytics
- Supports rich notifications (images, actions)

**Cons:**
- Requires Firebase project setup
- Need to handle device token management

**Cost:** Free for most use cases (up to unlimited messages)

---

### Option B: Web Push API (Service Workers)
**Best for:** Web-only applications

**Pros:**
- Native browser support
- No third-party dependencies
- Works offline
- Free

**Cons:**
- Web-only (no mobile native apps)
- More complex implementation
- Browser compatibility considerations

---

### Option C: OneSignal
**Best for:** Multi-platform with advanced features

**Pros:**
- Easy integration
- Great dashboard
- Supports all platforms
- Rich analytics

**Cons:**
- Free tier has limitations
- Paid plans for high volume

---

### Option D: Pusher Beams
**Best for:** Real-time notifications with WebSocket support

**Pros:**
- Real-time delivery
- Easy integration
- Good documentation

**Cons:**
- Paid service (free tier limited)
- More expensive at scale

---

## 2. Recommended Architecture: FCM (Firebase Cloud Messaging)

### Why FCM?
1. **Cross-platform**: Works on web, iOS, and Android
2. **Free**: No cost for typical usage
3. **Reliable**: Google's infrastructure
4. **Scalable**: Handles millions of notifications
5. **Rich features**: Images, actions, data payloads

---

## 3. Database Schema Changes

### New Table: `device_tokens`

```sql
CREATE TABLE device_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL,
    platform VARCHAR(20) NOT NULL, -- 'web', 'ios', 'android'
    device_info JSONB, -- Optional: device name, OS version, etc.
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, token)
);

CREATE INDEX idx_device_tokens_user_id ON device_tokens(user_id);
CREATE INDEX idx_device_tokens_active ON device_tokens(user_id, is_active) WHERE is_active = TRUE;
```

**Why this schema?**
- Users can have multiple devices (phone, tablet, desktop)
- Track which platform for platform-specific notifications
- Mark tokens as inactive when user logs out or uninstalls
- Store device info for debugging

---

## 4. Implementation Steps

### Step 1: Install Required Dependencies

Add to `requirements.txt`:
```txt
firebase-admin==6.2.0
pyfcm==1.5.2  # Alternative: simpler FCM client
```

Or use Firebase Admin SDK (recommended):
```bash
pip install firebase-admin
```

---

### Step 2: Create Device Token Model

**File: `app/models/device_token.py`**

```python
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database import Base
import uuid

class DeviceToken(Base):
    __tablename__ = "device_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String, nullable=False)
    platform = Column(String(20), nullable=False)  # 'web', 'ios', 'android'
    device_info = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        {'postgresql_partition_by': 'RANGE (created_at)'},  # Optional: for large scale
    )

    def __repr__(self):
        return f"<DeviceToken(user_id={self.user_id}, platform={self.platform})>"
```

---

### Step 3: Create Push Notification Service

**File: `app/services/push_notification_service.py`**

```python
import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.device_token import DeviceToken
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

class PushNotificationService:
    def __init__(self):
        # Initialize Firebase Admin SDK
        # You'll need to download service account key from Firebase Console
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("path/to/serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            self.fcm_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize FCM: {e}")
            self.fcm_initialized = False

    def send_expense_notification(
        self,
        db: Session,
        recipient_user_id: str,
        expense_creator_name: str,
        expense_amount: float,
        expense_description: str,
        expense_id: str
    ):
        """
        Send push notification when friend adds expense
        """
        if not self.fcm_initialized:
            logger.warning("FCM not initialized, skipping notification")
            return

        # Get all active device tokens for the recipient
        device_tokens = db.query(DeviceToken).filter(
            DeviceToken.user_id == recipient_user_id,
            DeviceToken.is_active == True
        ).all()

        if not device_tokens:
            logger.info(f"No device tokens found for user {recipient_user_id}")
            return

        # Prepare notification message
        notification = messaging.Notification(
            title="New Expense Added",
            body=f"{expense_creator_name} added ₹{expense_amount:.2f} - {expense_description}"
        )

        # Prepare data payload (for app to handle)
        data = {
            "type": "expense_added",
            "expense_id": str(expense_id),
            "friend_id": str(recipient_user_id),
            "amount": str(expense_amount),
            "description": expense_description
        }

        # Send to all devices
        tokens = [dt.token for dt in device_tokens]
        
        # Use multicast for multiple tokens
        if len(tokens) == 1:
            message = messaging.Message(
                notification=notification,
                data=data,
                token=tokens[0]
            )
            try:
                response = messaging.send(message)
                logger.info(f"Successfully sent notification: {response}")
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
        else:
            # Multicast for multiple devices
            message = messaging.MulticastMessage(
                notification=notification,
                data=data,
                tokens=tokens
            )
            try:
                response = messaging.send_multicast(message)
                logger.info(f"Successfully sent {response.success_count} notifications")
                if response.failure_count > 0:
                    logger.warning(f"Failed to send {response.failure_count} notifications")
                    # Handle failed tokens (mark as inactive)
                    self._handle_failed_tokens(db, tokens, response.responses)
            except Exception as e:
                logger.error(f"Error sending multicast notification: {e}")

    def _handle_failed_tokens(self, db: Session, tokens: List[str], responses: List):
        """
        Mark tokens as inactive if they fail (user uninstalled app, etc.)
        """
        for idx, response in enumerate(responses):
            if not response.success:
                if response.exception.code == 'messaging/invalid-registration-token' or \
                   response.exception.code == 'messaging/registration-token-not-registered':
                    # Token is invalid, mark as inactive
                    db.query(DeviceToken).filter(
                        DeviceToken.token == tokens[idx]
                    ).update({"is_active": False})
                    db.commit()
                    logger.info(f"Marked token as inactive: {tokens[idx]}")

# Singleton instance
push_notification_service = PushNotificationService()
```

---

### Step 4: Create Device Token Router

**File: `app/routers/device_tokens.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.device_token import DeviceToken
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

router = APIRouter(prefix="/device-tokens", tags=["Device Tokens"])

class DeviceTokenCreate(BaseModel):
    token: str
    platform: str  # 'web', 'ios', 'android'
    device_info: Optional[dict] = None

class DeviceTokenResponse(BaseModel):
    id: UUID
    platform: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True

@router.post("", response_model=DeviceTokenResponse, status_code=status.HTTP_201_CREATED)
def register_device_token(
    token_data: DeviceTokenCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Register a device token for push notifications
    Called by frontend when user grants notification permission
    """
    # Check if token already exists
    existing_token = db.query(DeviceToken).filter(
        DeviceToken.user_id == current_user.id,
        DeviceToken.token == token_data.token
    ).first()

    if existing_token:
        # Update existing token
        existing_token.is_active = True
        existing_token.platform = token_data.platform
        existing_token.device_info = token_data.device_info
        db.commit()
        db.refresh(existing_token)
        return DeviceTokenResponse.from_orm(existing_token)

    # Create new token
    new_token = DeviceToken(
        user_id=current_user.id,
        token=token_data.token,
        platform=token_data.platform,
        device_info=token_data.device_info,
        is_active=True
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    return DeviceTokenResponse.from_orm(new_token)

@router.delete("/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
def unregister_device_token(
    token_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unregister a device token (user logged out or uninstalled app)
    """
    device_token = db.query(DeviceToken).filter(
        DeviceToken.id == token_id,
        DeviceToken.user_id == current_user.id
    ).first()

    if not device_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device token not found"
        )

    # Mark as inactive instead of deleting (for analytics)
    device_token.is_active = False
    db.commit()
    return None

@router.get("", response_model=list[DeviceTokenResponse])
def get_my_device_tokens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all device tokens for current user
    """
    tokens = db.query(DeviceToken).filter(
        DeviceToken.user_id == current_user.id,
        DeviceToken.is_active == True
    ).all()
    return [DeviceTokenResponse.from_orm(token) for token in tokens]
```

---

### Step 5: Integrate with Expense Creation

**Modify: `app/routers/expenses.py`**

Add notification trigger after expense creation:

```python
from app.services.push_notification_service import push_notification_service

@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new expense between current user and a friend
    """
    # ... existing validation code ...

    # Create expense
    new_expense = Expense(
        user_a_id=current_user.id,
        user_b_id=expense_data.friend_id,
        amount=Decimal(str(expense_data.amount)),
        description=expense_data.description,
        paid_by_user_id=expense_data.paid_by_user_id,
        expense_date=expense_data.expense_date
    )
    
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    # Send push notification to friend (async, don't block response)
    try:
        # Get friend user details
        friend_user = db.query(User).filter(User.id == expense_data.friend_id).first()
        
        if friend_user:
            push_notification_service.send_expense_notification(
                db=db,
                recipient_user_id=str(expense_data.friend_id),
                expense_creator_name=current_user.name or current_user.email,
                expense_amount=float(expense_data.amount),
                expense_description=expense_data.description,
                expense_id=str(new_expense.id)
            )
    except Exception as e:
        # Log error but don't fail the expense creation
        logger.error(f"Failed to send push notification: {e}")

    return ExpenseResponse.from_orm_expense(new_expense)
```

---

### Step 6: Create Database Migration

**File: `alembic/versions/xxxx_add_device_tokens_table.py`**

```python
"""Add device tokens table

Revision ID: xxxx
Revises: 74f7ca8b76b3
Create Date: 2025-01-XX XX:XX:XX.XXXXXX
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'xxxx'
down_revision = '74f7ca8b76b3'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'device_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('platform', sa.String(20), nullable=False),
        sa.Column('device_info', postgresql.JSONB(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'token', name='_user_token_uc')
    )
    op.create_index('idx_device_tokens_user_id', 'device_tokens', ['user_id'])
    op.create_index('idx_device_tokens_active', 'device_tokens', ['user_id', 'is_active'], 
                    postgresql_where=sa.text('is_active = true'))

def downgrade():
    op.drop_index('idx_device_tokens_active', table_name='device_tokens')
    op.drop_index('idx_device_tokens_user_id', table_name='device_tokens')
    op.drop_table('device_tokens')
```

---

## 5. Frontend Integration (Overview)

### Web Push Setup (React/Next.js)

1. **Request Notification Permission**
```javascript
// Request permission
const requestNotificationPermission = async () => {
  const permission = await Notification.requestPermission();
  if (permission === 'granted') {
    // Get FCM token from Firebase SDK
    const token = await getMessaging().getToken({ vapidKey: VAPID_KEY });
    
    // Register token with backend
    await fetch('/api/device-tokens', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        token: token,
        platform: 'web',
        device_info: {
          userAgent: navigator.userAgent,
          language: navigator.language
        }
      })
    });
  }
};
```

2. **Handle Incoming Notifications**
```javascript
// Listen for foreground notifications
onMessage(messaging, (payload) => {
  console.log('Message received:', payload);
  // Show notification
  new Notification(payload.notification.title, {
    body: payload.notification.body,
    icon: '/icon.png'
  });
  
  // Navigate to expense detail if clicked
  // Handle navigation based on payload.data
});
```

---

## 6. Environment Variables

Add to `.env`:
```env
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=./firebase-service-account-key.json
# Or use base64 encoded JSON
FIREBASE_SERVICE_ACCOUNT_KEY_BASE64=...
```

---

## 7. Firebase Setup Steps

1. **Create Firebase Project**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create new project
   - Enable Cloud Messaging API

2. **Generate Service Account Key**
   - Project Settings → Service Accounts
   - Generate new private key
   - Download JSON file
   - Store securely (don't commit to git)

3. **Web App Configuration**
   - Add web app to Firebase project
   - Copy config (apiKey, authDomain, etc.)
   - Use in frontend

4. **VAPID Key** (for web)
   - Cloud Messaging → Web Push certificates
   - Generate key pair
   - Use in frontend for token generation

---

## 8. Best Practices

### Security
- ✅ Store Firebase service account key securely (environment variable or secret manager)
- ✅ Validate device tokens on backend
- ✅ Only send notifications to authenticated users
- ✅ Rate limit notification endpoints

### Performance
- ✅ Send notifications asynchronously (don't block expense creation)
- ✅ Use background tasks (Celery, FastAPI BackgroundTasks)
- ✅ Batch notifications for multiple devices
- ✅ Cache user device tokens if needed

### User Experience
- ✅ Allow users to disable notifications in settings
- ✅ Provide clear notification content
- ✅ Deep link to relevant expense when notification clicked
- ✅ Handle notification permission gracefully

### Error Handling
- ✅ Log all notification failures
- ✅ Mark invalid tokens as inactive
- ✅ Retry failed notifications (with exponential backoff)
- ✅ Monitor notification delivery rates

---

## 9. Alternative: Background Task Queue

For better scalability, use a task queue:

**Option: Celery + Redis**
```python
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379')

@celery_app.task
def send_expense_notification_task(recipient_id, creator_name, amount, description, expense_id):
    # Send notification logic here
    pass

# In expense router:
send_expense_notification_task.delay(...)
```

**Option: FastAPI BackgroundTasks**
```python
from fastapi import BackgroundTasks

@router.post("")
def create_expense(
    expense_data: ExpenseCreate,
    background_tasks: BackgroundTasks,
    ...
):
    # ... create expense ...
    
    background_tasks.add_task(
        push_notification_service.send_expense_notification,
        db=db,
        recipient_user_id=str(expense_data.friend_id),
        ...
    )
```

---

## 10. Testing Strategy

### Unit Tests
- Test notification service with mock FCM
- Test device token registration
- Test token cleanup on failures

### Integration Tests
- Test expense creation triggers notification
- Test notification delivery
- Test multiple device tokens

### Manual Testing
1. Register device token
2. Create expense as User A
3. Verify User B receives notification
4. Test notification click navigation
5. Test notification on multiple devices

---

## 11. Monitoring & Analytics

### Metrics to Track
- Notification delivery rate
- Notification open rate
- Failed token count
- Notification latency
- User engagement

### Tools
- Firebase Console Analytics
- Custom logging
- Application Performance Monitoring (APM)

---

## 12. Cost Considerations

### FCM Pricing
- **Free tier**: Unlimited messages
- **No cost** for typical usage
- Only pay for Firebase hosting/other services

### Infrastructure
- Database storage for device tokens (minimal)
- Background task processing (if using Celery)

---

## 13. Implementation Checklist

- [ ] Set up Firebase project
- [ ] Download service account key
- [ ] Create device_tokens table migration
- [ ] Create DeviceToken model
- [ ] Create push notification service
- [ ] Create device token router
- [ ] Integrate with expense creation
- [ ] Add environment variables
- [ ] Test notification delivery
- [ ] Frontend: Request notification permission
- [ ] Frontend: Register device token
- [ ] Frontend: Handle incoming notifications
- [ ] Add error handling and logging
- [ ] Set up monitoring
- [ ] Document API endpoints

---

## 14. Future Enhancements

1. **Notification Preferences**
   - Allow users to disable specific notification types
   - Quiet hours
   - Notification frequency settings

2. **Rich Notifications**
   - Expense images
   - Action buttons (View, Acknowledge)
   - Grouped notifications

3. **Notification History**
   - Store sent notifications
   - Mark as read/unread
   - Notification center in app

4. **Multi-language Support**
   - Localized notification messages
   - Currency formatting

---

## 15. Troubleshooting

### Common Issues

**Issue: Notifications not received**
- Check device token is registered
- Verify Firebase service account key
- Check notification permissions
- Review Firebase Console logs

**Issue: Invalid token errors**
- Tokens expire, handle gracefully
- Mark invalid tokens as inactive
- Prompt user to re-register

**Issue: High latency**
- Use background tasks
- Consider message queue
- Optimize database queries

---

## Conclusion

Implementing push notifications with FCM provides a robust, scalable solution for notifying users when friends add expenses. The architecture outlined above ensures:

- ✅ Reliable delivery
- ✅ Cross-platform support
- ✅ Scalability
- ✅ Good user experience
- ✅ Maintainable code

Start with the basic implementation and iterate based on user feedback and analytics.

---

## Resources

- [Firebase Cloud Messaging Documentation](https://firebase.google.com/docs/cloud-messaging)
- [FCM Admin SDK Python](https://firebase.google.com/docs/reference/admin/python/firebase_admin.messaging)
- [Web Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

---

**Last Updated:** January 2025
**Author:** AI Assistant
**Status:** Draft - Ready for Implementation

