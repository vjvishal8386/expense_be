import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.device_token import DeviceToken
from app.models.user import User
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
_fcm_initialized = False

def initialize_fcm():
    """Initialize Firebase Admin SDK"""
    global _fcm_initialized
    
    if _fcm_initialized:
        return True
    
    try:
        # Check if Firebase is already initialized
        if firebase_admin._apps:
            _fcm_initialized = True
            return True
        
        # Try to find Firebase service account key
        # Option 1: Environment variable with file path
        firebase_key_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
        
        # Option 2: Default filename in project root
        if not firebase_key_path:
            default_path = Path(__file__).parent.parent.parent / "VJ-spendbook-687bc-firebase-adminsdk-fbsvc-8b5f1c89a8.json"
            if default_path.exists():
                firebase_key_path = str(default_path)
        
        if not firebase_key_path or not Path(firebase_key_path).exists():
            logger.warning("Firebase service account key not found. Push notifications will be disabled.")
            return False
        
        cred = credentials.Certificate(firebase_key_path)
        firebase_admin.initialize_app(cred)
        _fcm_initialized = True
        logger.info("Firebase Admin SDK initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
        return False


def subscribe_token_to_topic(token: str, topic: str):
    """Subscribe a device token to a topic (for group notifications)"""
    if not initialize_fcm():
        return 0
    
    try:
        response = messaging.subscribe_to_topic([token], topic)
        return response.success_count
    except Exception as e:
        logger.error(f"Error subscribing token to topic: {e}")
        return 0


def send_project_alert(topic: str, title: str, body: str, data: dict = None):
    """Send notification to a topic (for group/project notifications)"""
    if not initialize_fcm():
        return None
    
    try:
        message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
            data=data or {},
        topic=topic,
        )
        return messaging.send(message)
    except Exception as e:
        logger.error(f"Error sending topic notification: {e}")
        return None


def send_expense_notification(
    db: Session,
    recipient_user_id: str,
    expense_creator_name: str,
    expense_amount: float,
    expense_description: str,
    expense_id: str,
    friend_id: str
):
    """
    Send push notification when friend adds expense
    
    Args:
        db: Database session
        recipient_user_id: UUID of user who should receive notification
        expense_creator_name: Name of user who created the expense
        expense_amount: Amount of the expense
        expense_description: Description of the expense
        expense_id: UUID of the expense
        friend_id: UUID of the friend (expense creator)
    """
    if not initialize_fcm():
        logger.warning("FCM not initialized, skipping notification")
        return
    
    try:
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
        
        # Prepare data payload (for app to handle navigation)
        data = {
            "type": "expense_added",
            "expense_id": str(expense_id),
            "friend_id": str(friend_id),
            "amount": str(expense_amount),
            "description": expense_description
        }
        
        # Send to all devices
        tokens = [dt.token for dt in device_tokens]
        
        if len(tokens) == 1:
            # Single device
            message = messaging.Message(
                notification=notification,
                data=data,
                token=tokens[0]
            )
            try:
                response = messaging.send(message)
                logger.info(f"Successfully sent notification: {response}")
            except messaging.UnregisteredError:
                # Token is invalid, mark as inactive
                db.query(DeviceToken).filter(
                    DeviceToken.token == tokens[0]
                ).update({"is_active": False})
                db.commit()
                logger.warning(f"Marked invalid token as inactive: {tokens[0]}")
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
        else:
            # Multiple devices - use multicast
            message = messaging.MulticastMessage(
                notification=notification,
                data=data,
                tokens=tokens
            )
            try:
                response = messaging.send_multicast(message)
                logger.info(f"Successfully sent {response.success_count}/{len(tokens)} notifications")
                
                # Handle failed tokens
                if response.failure_count > 0:
                    for idx, resp in enumerate(response.responses):
                        if not resp.success:
                            error_code = resp.exception.code if resp.exception else None
                            if error_code in ['messaging/invalid-registration-token', 
                                             'messaging/registration-token-not-registered']:
                                # Mark invalid token as inactive
                                db.query(DeviceToken).filter(
                                    DeviceToken.token == tokens[idx]
                                ).update({"is_active": False})
                                logger.warning(f"Marked invalid token as inactive: {tokens[idx]}")
                    db.commit()
                    
            except Exception as e:
                logger.error(f"Error sending multicast notification: {e}")
                
    except Exception as e:
        logger.error(f"Error in send_expense_notification: {e}")
