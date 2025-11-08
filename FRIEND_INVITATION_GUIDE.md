# Friend Invitation System - Complete Guide

Complete guide for the friend invitation feature with email invites and automatic friend linking.

## 📋 Overview

The friend invitation system supports two scenarios:

1. **Inviting existing user**: Sends friend request notification, instantly connects as friends
2. **Inviting new user**: Sends invitation email with registration link that automatically adds friendship

---

## Features

✅ **Email Invitations** - Send personalized invitation emails  
✅ **Automatic Friend Linking** - Invitation token auto-creates friendship on registration  
✅ **Smart Detection** - Automatically detects if invitee already has account  
✅ **Secure Tokens** - Invitation tokens expire after 7 days  
✅ **Bidirectional Friendship** - Both users see each other as friends  
✅ **Email Notifications** - Notifications for friend requests and invitations  

---

## API Endpoints

### 1. Invite Friend

**Endpoint**: `POST /friends/invite`  
**Authentication**: Required (JWT Bearer token)

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "name": "Jane Smith"  // optional
}
```

**Response (Friend Exists):**
```json
{
  "message": "Friend request sent to friend@example.com",
  "invitation_sent": true,
  "friend_exists": true,
  "friend": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "friend@example.com",
    "name": "Friend Name",
    "email_verified": true
  }
}
```

**Response (New Invitation):**
```json
{
  "message": "Invitation sent to newuser@example.com. They will be added as your friend when they sign up.",
  "invitation_sent": true,
  "friend_exists": false,
  "friend": null
}
```

---

## Invitation Flow

### Scenario 1: Inviting Existing User

```
1. User A invites User B via email
   ↓
2. System checks: User B already has account
   ↓
3. System creates bidirectional friendship
   ↓
4. System sends notification email to User B
   ↓
5. User B sees User A in their friends list
```

### Scenario 2: Inviting New User

```
1. User A invites new user via email
   ↓
2. System checks: Email not registered
   ↓
3. System creates invitation with token
   ↓
4. System sends invitation email with registration link
   ↓
5. New user clicks link → Registers with invitation token
   ↓
6. System automatically creates friendship during registration
   ↓
7. Both users are now friends
```

---

## Email Templates

### Invitation Email (New User)

**Subject**: `{inviter_name} invited you to join Expense Tracker!`

**Body**:
```
Hi there!

{inviter_name} has invited you to join Expense Tracker to manage shared expenses together!

Click the link below to sign up and automatically become friends with {inviter_name}:

http://localhost:3000/register?invitation={invitation_token}

This invitation will expire in 7 days.

If you didn't expect this invitation, you can safely ignore this email.

Best regards,
Expense Tracker Team
```

### Friend Request Notification (Existing User)

**Subject**: `{requester_name} added you as a friend on Expense Tracker`

**Body**:
```
Hi {name},

Great news! {requester_name} has added you as a friend on Expense Tracker.

You can now share and track expenses with {requester_name}.

Login to your account to start managing shared expenses:
http://localhost:3000/login

Best regards,
Expense Tracker Team
```

---

## Registration with Invitation Token

When a user clicks the invitation link, they land on:
```
http://localhost:3000/register?invitation={token}
```

The frontend should:
1. Extract `invitation` parameter from URL
2. Include it in registration request
3. Auto-create friendship after registration

**Registration Request with Invitation:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "name": "Jane Smith",
  "invitation_token": "abc123xyz789"
}
```

**Registration Response:**
```json
{
  "message": "Registration successful! Please check your email for OTP verification code.",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "newuser@example.com",
  "email_verified": false
}
```

**What Happens Behind the Scenes:**
1. User registers with email/password
2. System validates invitation token
3. System creates user account
4. System creates bidirectional friendship with inviter
5. System marks invitation as accepted
6. System sends OTP for email verification
7. After OTP verification, user is logged in and already has inviter as friend

---

## Frontend Integration

### TypeScript Types

Create `src/types/friend.ts`:

```typescript
export interface FriendInviteRequest {
  email: string;
  name?: string;
}

export interface Friend {
  id: string;
  email: string;
  name?: string;
  email_verified: boolean;
}

export interface FriendInviteResponse {
  message: string;
  invitation_sent: boolean;
  friend_exists: boolean;
  friend?: Friend;
}
```

### API Service

Create `src/api/friendService.ts`:

```typescript
import api from './axios';
import type { FriendInviteRequest, FriendInviteResponse, Friend } from '../types/friend';

export const friendService = {
  /**
   * Invite a friend by email
   */
  async inviteFriend(data: FriendInviteRequest): Promise<FriendInviteResponse> {
    const response = await api.post<FriendInviteResponse>('/friends/invite', data);
    return response.data;
  },

  /**
   * Get all friends
   */
  async getFriends(): Promise<Friend[]> {
    const response = await api.get<Friend[]>('/friends');
    return response.data;
  },
};
```

### React Component: Invite Friend

```typescript
import React, { useState } from 'react';
import { friendService } from '../api/friendService';

const InviteFriend: React.FC = () => {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);

    try {
      const response = await friendService.inviteFriend({ email, name });
      setMessage(response.message);
      setEmail('');
      setName('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send invitation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="invite-friend-container">
      <h2>Invite a Friend</h2>
      {error && <div className="error">{error}</div>}
      {message && <div className="success">{message}</div>}

      <form onSubmit={handleInvite}>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="friend@example.com"
            required
          />
        </div>

        <div>
          <label>Name (optional):</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Friend's name"
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send Invitation'}
        </button>
      </form>
    </div>
  );
};

export default InviteFriend;
```

### React Component: Registration with Invitation

```typescript
import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { authService } from '../api/authService';

const Register: React.FC = () => {
  const [searchParams] = useSearchParams();
  const invitationToken = searchParams.get('invitation');
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    invitation_token: invitationToken || undefined,
  });

  useEffect(() => {
    if (invitationToken) {
      // Show message that user was invited
      console.log('Registering via invitation');
    }
  }, [invitationToken]);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    // Include invitation_token in registration
    const response = await authService.register(formData);
    // Handle response...
  };

  return (
    <div>
      {invitationToken && (
        <div className="info">
          You were invited to join! Complete registration to connect with your friend.
        </div>
      )}
      <form onSubmit={handleRegister}>
        {/* Registration form fields */}
      </form>
    </div>
  );
};
```

---

## Backend Implementation Details

### Invitation Service

Location: `app/services/invitation_service.py`

**Key Methods:**
- `create_invitation()` - Creates invitation with secure token
- `get_invitation_by_token()` - Retrieves and validates invitation
- `accept_invitation()` - Marks invitation as accepted
- `get_inviter()` - Gets inviter user information

**Features:**
- Secure token generation (32 characters)
- 7-day expiration
- Reuses existing valid invitations
- Automatic cleanup of expired invitations

### Email Service Updates

Location: `app/services/email_service.py`

**New Methods:**
- `send_friend_invitation_email()` - Sends invitation with registration link
- `send_friend_request_notification()` - Notifies existing users of friend request

**Features:**
- Development mode (prints to console if SMTP not configured)
- Personalized email templates
- Configurable frontend URL

### Database Schema

**friend_invitations Table:**
```sql
CREATE TABLE friend_invitations (
  id UUID PRIMARY KEY,
  inviter_id UUID REFERENCES users(id) ON DELETE CASCADE,
  invitee_email VARCHAR NOT NULL,
  invitation_token VARCHAR UNIQUE NOT NULL,
  accepted BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX ix_friend_invitations_inviter_id ON friend_invitations(inviter_id);
CREATE INDEX ix_friend_invitations_invitee_email ON friend_invitations(invitee_email);
CREATE INDEX ix_friend_invitations_invitation_token ON friend_invitations(invitation_token);
```

---

## Testing

### Test Scenario 1: Invite Existing User

```bash
# 1. Login as User A
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"usera@example.com","password":"password123"}'

# Save token as TOKEN_A

# 2. Invite User B (who already exists)
curl -X POST http://127.0.0.1:8000/friends/invite \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"email":"userb@example.com","name":"User B"}'

# 3. Check friends list
curl -X GET http://127.0.0.1:8000/friends \
  -H "Authorization: Bearer $TOKEN_A"
```

### Test Scenario 2: Invite New User

```bash
# 1. Login as User A
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"usera@example.com","password":"password123"}'

# Save token as TOKEN_A

# 2. Invite new user
curl -X POST http://127.0.0.1:8000/friends/invite \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com","name":"New User"}'

# 3. Check console for invitation link (in development mode)
# Link format: http://localhost:3000/register?invitation={token}

# 4. Register new user with invitation token
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"newuser@example.com",
    "password":"password123",
    "name":"New User",
    "invitation_token":"INVITATION_TOKEN_FROM_EMAIL"
  }'

# 5. Verify OTP and login as new user

# 6. Check friends list - should include User A
curl -X GET http://127.0.0.1:8000/friends \
  -H "Authorization: Bearer $TOKEN_NEWUSER"
```

---

## Environment Variables

Add to `.env`:

```bash
# Frontend URL (for invitation links)
FRONTEND_URL=http://localhost:3000

# Email Configuration (existing)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
```

**Production:**
```bash
FRONTEND_URL=https://your-domain.com
```

---

## Error Handling

### Common Errors

**Cannot invite yourself:**
```json
{
  "detail": "Cannot invite yourself"
}
```

**Already friends:**
```json
{
  "detail": "You are already friends with this user"
}
```

**Invalid invitation token:**
- Token not found
- Token expired (> 7 days)
- Token already accepted

**Email sending failed:**
- Invitation still created
- Link printed to console in development mode

---

## Security Considerations

1. **Token Security**
   - Tokens are cryptographically secure (32 characters)
   - Tokens expire after 7 days
   - One-time use (marked as accepted after registration)

2. **Email Validation**
   - Emails are normalized (lowercased, trimmed)
   - Duplicate prevention

3. **Authorization**
   - Only authenticated users can send invitations
   - Users cannot invite themselves

4. **Database Integrity**
   - Foreign key constraints
   - Unique token constraint
   - Cascade delete on user deletion

---

## Production Recommendations

1. **Email Service**: Use proper email service (SendGrid, AWS SES, etc.)
2. **Rate Limiting**: Limit invitation sends per user per day
3. **Analytics**: Track invitation acceptance rate
4. **Cleanup**: Periodically delete expired invitations
5. **Notifications**: Add in-app notifications for friend requests
6. **Rich Emails**: Use HTML templates with styling
7. **Deep Links**: Support mobile deep links for invitation URLs

---

## Summary

✅ **Two-mode system**: Handles both existing and new users  
✅ **Email invitations**: Personalized invitation emails with registration links  
✅ **Automatic friendship**: Invitation token auto-creates bidirectional friendship  
✅ **Secure tokens**: Cryptographically secure, expiring tokens  
✅ **Notification system**: Email notifications for all friend actions  
✅ **Development-friendly**: Console fallback when SMTP not configured  

The friend invitation system provides a seamless way to grow your user base while automatically establishing friend relationships.

