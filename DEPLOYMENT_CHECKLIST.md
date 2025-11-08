# Deployment Checklist - New Features

## 🚀 Features Added (Ready to Deploy)

✅ **Email Verification with OTP**
- User registration with email verification
- OTP sent to email (6-digit code)
- OTP expiration (10 minutes)
- Resend OTP functionality

✅ **Friend Invitation System**
- Invite friends via email
- Automatic friend linking with invitation tokens
- Email notifications for friend requests
- Support for inviting non-registered users

✅ **Enhanced Security**
- Password validation (minimum 8 characters)
- Email normalization
- Transaction rollback on errors

---

## 📋 Pre-Deployment Checklist

### 1. Database Migration Required ✅

New tables need to be created:
- [x] `email_verified` field added to `users` table
- [x] `friend_invitations` table created

**Action Required**: Run migrations on Render after deployment

### 2. Environment Variables Required 🔧

Add these to your Render Dashboard → Environment:

```bash
# Email Configuration (Required for OTP and Invitations)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=dev.nexonx@gmail.com
SMTP_PASSWORD=yztk gypu wtyu rmwg
FROM_EMAIL=dev.nexonx@gmail.com

# Frontend URL (Required for invitation links)
FRONTEND_URL=https://expense-fe-chi.vercel.app
```

⚠️ **Note**: If SMTP is not configured, OTPs will not be sent (system will fail gracefully)

### 3. Files Changed

Modified Files:
- ✅ `app/models/user.py` - Added email_verified field
- ✅ `app/models/__init__.py` - Added FriendInvitation import
- ✅ `app/models/invitation.py` - New invitation model
- ✅ `app/routers/auth.py` - OTP verification flow
- ✅ `app/routers/friends.py` - Invitation system
- ✅ `app/schemas/auth.py` - Updated schemas
- ✅ `app/schemas/friend.py` - New invitation schemas
- ✅ `app/services/email_service.py` - Email sending service
- ✅ `app/services/otp_service.py` - OTP generation/verification
- ✅ `app/services/invitation_service.py` - Invitation management
- ✅ `alembic/versions/` - New migrations
- ✅ `render.yaml` - Updated environment variables

---

## 🔄 Deployment Steps

### Step 1: Commit and Push Changes

```bash
# Navigate to project directory
cd /home/vishal/Downloads/temp_BE

# Check what changed
git status

# Add all changes
git add .

# Commit with descriptive message
git commit -m "feat: Add email verification with OTP and friend invitation system

- Add email verification with OTP during registration
- Implement friend invitation system with email invites
- Add automatic friend linking via invitation tokens
- Update database schema with email_verified and friend_invitations
- Add email service for OTP and invitation emails
- Update environment variables for SMTP and frontend URL"

# Push to GitHub
git push origin main
```

### Step 2: Configure Environment Variables on Render

1. Go to Render Dashboard: https://dashboard.render.com
2. Select your service: **expense-tracker-api**
3. Go to **Environment** tab
4. Add the following variables:

| Key | Value | Notes |
|-----|-------|-------|
| `SMTP_SERVER` | `smtp.gmail.com` | Gmail SMTP server |
| `SMTP_PORT` | `587` | TLS port |
| `SMTP_USERNAME` | `dev.nexonx@gmail.com` | Your Gmail |
| `SMTP_PASSWORD` | `yztk gypu wtyu rmwg` | Gmail App Password |
| `FROM_EMAIL` | `dev.nexonx@gmail.com` | Sender email |
| `FRONTEND_URL` | `https://expense-fe-chi.vercel.app` | Your frontend URL |

5. Click **Save Changes**

### Step 3: Trigger Deployment

Render will automatically deploy when you push to main branch.

**Monitor deployment**:
1. Go to **Events** tab in Render Dashboard
2. Wait for "Build succeeded" message
3. Check **Logs** tab for any errors

### Step 4: Run Database Migrations

Once deployed, run migrations:

1. Go to Render Dashboard → Your Service
2. Click **Shell** tab
3. Run:
```bash
alembic upgrade head
```

4. Verify migration:
```bash
# Check if tables exist
python -c "from app.database import engine; from sqlalchemy import inspect; inspector = inspect(engine); print('Tables:', inspector.get_table_names())"
```

### Step 5: Verify Deployment

Test the new endpoints:

**1. Health Check:**
```bash
curl https://your-api.onrender.com/health
```

**2. Test Registration with OTP:**
```bash
curl -X POST https://your-api.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

**3. Check API Documentation:**
Visit: `https://your-api.onrender.com/docs`

**4. Test Friend Invitation:**
Login and try the new `/friends/invite` endpoint

---

## 🔍 Post-Deployment Verification

### Check 1: Database Schema
- [ ] `users` table has `email_verified` column
- [ ] `friend_invitations` table exists
- [ ] All migrations applied successfully

### Check 2: Email Functionality
- [ ] Registration sends OTP email
- [ ] Friend invitations send email
- [ ] Email templates render correctly

### Check 3: API Endpoints
- [ ] `POST /auth/register` returns user_id and message
- [ ] `POST /auth/verify-otp` activates account
- [ ] `POST /auth/resend-otp` resends OTP
- [ ] `POST /friends/invite` sends invitations
- [ ] All endpoints return proper responses

### Check 4: Error Handling
- [ ] Invalid OTP shows proper error
- [ ] Expired OTP shows proper error
- [ ] Duplicate friend request handled
- [ ] Self-invitation prevented

---

## 🚨 Troubleshooting

### Issue: Migrations Failed

**Solution:**
```bash
# In Render Shell
alembic downgrade -1
alembic upgrade head
```

### Issue: Email Not Sending

**Check:**
1. SMTP credentials are correct
2. Gmail App Password (not regular password)
3. 2-Step Verification enabled on Gmail
4. Check Render logs for SMTP errors

**Fallback:**
- System will print OTP to logs if SMTP fails
- Check Render Logs tab for OTP codes during testing

### Issue: Friend Invitations Not Working

**Check:**
1. `FRONTEND_URL` is set correctly
2. Invitation tokens are being generated
3. Database has `friend_invitations` table
4. Check Render logs for invitation links

### Issue: Import Errors

**Solution:**
```bash
# In Render Shell
pip install --upgrade -r requirements.txt
```

---

## 📊 Migration Status

### Migration 1: Add email_verified field
- **File**: `43933116c651_add_email_verified_field_to_users.py`
- **Status**: ✅ Ready
- **Changes**: Adds `email_verified` BOOLEAN column to `users` table

### Migration 2: Add friend_invitations table
- **File**: `74f7ca8b76b3_add_friend_invitations_table.py`
- **Status**: ✅ Ready
- **Changes**: Creates `friend_invitations` table with indexes

---

## 🔐 Security Notes

1. **SMTP Credentials**: Never commit SMTP passwords to git
2. **Invitation Tokens**: 32-character secure tokens with 7-day expiration
3. **OTP Security**: 6-digit OTPs with 10-minute expiration and max 5 attempts
4. **Email Verification**: Users must verify email before login

---

## 📱 Frontend Updates Required

Your frontend needs to be updated to support:

1. **Registration Flow**:
   - Show OTP input screen after registration
   - Add "Resend OTP" button
   - Handle verification before login

2. **Friend Invitation**:
   - Add "Invite Friend" button/form
   - Handle invitation URL parameter: `?invitation={token}`
   - Show invitation message during registration

3. **Updated Documentation**:
   - See `FRONTEND_AUTH_INTEGRATION.md`
   - See `FRIEND_INVITATION_GUIDE.md`

---

## ✅ Deployment Complete Checklist

After deployment, verify:

- [ ] API is accessible at Render URL
- [ ] Health endpoint returns 200 OK
- [ ] Swagger docs load correctly
- [ ] Database migrations completed
- [ ] Environment variables configured
- [ ] Registration creates users
- [ ] OTP emails are being sent (or printed to logs)
- [ ] Friend invitations work
- [ ] Existing features still work (login, friends, expenses)
- [ ] CORS allows your frontend domain
- [ ] No errors in Render logs

---

## 🎯 Summary

**What's Deployed:**
- Email verification with OTP system
- Friend invitation system with email invites
- Enhanced security and error handling
- Database schema updates

**Breaking Changes:**
- ⚠️ Login now requires email verification
- ⚠️ Users registered before this update will need to verify email

**Next Steps:**
1. Push code to GitHub
2. Add environment variables on Render
3. Wait for auto-deployment
4. Run migrations
5. Test all endpoints
6. Update frontend to support new features

**Documentation:**
- `FRONTEND_AUTH_INTEGRATION.md` - Frontend integration guide
- `FRIEND_INVITATION_GUIDE.md` - Friend invitation system guide
- `OTP_IMPLEMENTATION.md` - OTP system details

---

## 📞 Need Help?

- Check Render Logs for errors
- Test locally first if unsure
- Review API documentation at `/docs`
- Verify environment variables are set correctly

Good luck with deployment! 🚀

