# OTP Email Verification Implementation

## Overview

This implementation adds **email verification with OTP (One-Time Password)** during user registration. The system uses a two-step authentication flow:

1. **Registration**: User registers with email/password → OTP sent to email
2. **Verification**: User verifies OTP → Account activated → JWT token returned
3. **Login**: User can now login with password (email must be verified)

## Why This Approach?

**Email Verification + Password Authentication** is the **best solution** because:

✅ **Verifies email ownership** - Ensures users have access to their email  
✅ **Faster subsequent logins** - Users don't need email access every time  
✅ **Better security** - Password + verified email = stronger authentication  
✅ **Industry standard** - Used by most major platforms (Gmail, Facebook, etc.)  
✅ **Better UX** - Users can login quickly after initial verification  

**Alternative (Passwordless OTP-only):**
- ❌ Requires email access for every login
- ❌ Slower user experience
- ❌ Less convenient for frequent logins

## Architecture

### New Components

1. **Email Service** (`app/services/email_service.py`)
   - Sends OTP emails via SMTP
   - Falls back to console output in development mode

2. **OTP Service** (`app/services/otp_service.py`)
   - Generates 6-digit OTP codes
   - Stores OTPs with expiration (10 minutes)
   - Verifies OTP codes
   - Rate limiting (max 5 attempts per OTP)

3. **Database Changes**
   - Added `email_verified` field to User model (Boolean, default=False)

### API Endpoints

#### 1. Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "message": "Registration successful! Please check your email for OTP verification code.",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "email_verified": false
}
```

#### 2. Verify OTP
```http
POST /auth/verify-otp
Content-Type: application/json

{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "otp": "123456"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "name": "John Doe",
    "email_verified": true
  }
}
```

#### 3. Resend OTP
```http
POST /auth/resend-otp
Content-Type: application/json

{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "OTP has been resent to your email",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com"
}
```

#### 4. Login (Updated)
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Note:** Login now requires email to be verified. If not verified, returns 403 error with message to verify email.

## Environment Variables

Add these to your `.env` file:

```bash
# Email Configuration (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
```

### Gmail Setup

1. Enable 2-Step Verification on your Google account
2. Generate App Password:
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password as `SMTP_PASSWORD`

### Development Mode

If SMTP credentials are not configured, the system will:
- Print OTP to console: `[DEV MODE] OTP for user@example.com: 123456`
- Still allow registration and verification to work

## Database Migration

You need to create a migration for the new `email_verified` field:

```bash
# Generate migration
alembic revision --autogenerate -m "Add email_verified field to users"

# Review the migration file in alembic/versions/

# Apply migration
alembic upgrade head
```

Or manually add the field:

```sql
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE NOT NULL;
```

## Security Features

1. **OTP Expiration**: OTPs expire after 10 minutes
2. **Rate Limiting**: Max 5 verification attempts per OTP
3. **Password Validation**: Minimum 8 characters required
4. **Email Normalization**: Emails are lowercased and trimmed
5. **Transaction Safety**: Database rollback on errors

## Production Recommendations

1. **Use Redis for OTP Storage**: Replace in-memory storage with Redis
   ```python
   # In app/services/otp_service.py
   # Replace _otp_storage dict with Redis client
   ```

2. **Email Service Provider**: Consider using:
   - SendGrid
   - AWS SES
   - Mailgun
   - Resend

3. **Rate Limiting**: Add API rate limiting (e.g., `slowapi`)

4. **OTP Length**: Consider 6-8 digits (currently 6)

5. **Expiration Time**: Adjust based on your needs (currently 10 minutes)

## Testing Flow

1. **Register**:
   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123","name":"Test User"}'
   ```

2. **Check Email/Console** for OTP (e.g., `123456`)

3. **Verify OTP**:
   ```bash
   curl -X POST http://localhost:8000/auth/verify-otp \
     -H "Content-Type: application/json" \
     -d '{"user_id":"<user_id_from_register>","otp":"123456"}'
   ```

4. **Login**:
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}'
   ```

## Frontend Integration

### Registration Flow

```javascript
// Step 1: Register
const registerResponse = await fetch('/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123',
    name: 'John Doe'
  })
});

const { user_id, email } = await registerResponse.json();

// Step 2: Show OTP input form
// User enters OTP from email

// Step 3: Verify OTP
const verifyResponse = await fetch('/auth/verify-otp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: user_id,
    otp: otpCode
  })
});

const { access_token } = await verifyResponse.json();
// Store token and redirect to dashboard
```

## Troubleshooting

### OTP Not Received
- Check spam folder
- Verify SMTP credentials
- Check console output in development mode
- Use `/auth/resend-otp` endpoint

### OTP Expired
- OTPs expire after 10 minutes
- Use `/auth/resend-otp` to get a new one

### Email Already Verified
- User can login directly with password
- No need to verify again

### Login Fails with "Email not verified"
- User must verify email first
- Use `/auth/resend-otp` if OTP was lost

## Summary

✅ **Email verification with OTP** during registration  
✅ **Password-based authentication** after verification  
✅ **Secure OTP generation** with expiration  
✅ **Transaction safety** with rollback on errors  
✅ **Development-friendly** with console OTP output  
✅ **Production-ready** architecture (just add Redis for OTP storage)

This is the **best solution** for most applications as it balances security, user experience, and industry standards.

