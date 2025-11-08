# SendGrid Email Setup for Render

## 🚨 Why SendGrid?

Render's free tier **blocks outbound SMTP connections** (port 587/465) to prevent spam. This causes the error:

```
Error sending email: [Errno 101] Network is unreachable
```

**Solution**: Use SendGrid's API instead of SMTP. SendGrid works perfectly on Render!

---

## 🎯 Quick Setup (5 minutes)

### Step 1: Create SendGrid Account (FREE)

1. **Go to**: https://signup.sendgrid.com/
2. **Sign up** with your email
3. **Verify your email** (check inbox)
4. **Complete profile** (select "Free" plan)

**Free Tier**: 100 emails/day forever (perfect for your app!)

---

### Step 2: Create API Key

1. **Login to SendGrid**: https://app.sendgrid.com/
2. **Navigate to**: Settings → API Keys (left sidebar)
3. **Click**: "Create API Key"
4. **Name**: `expense-tracker-production`
5. **Permissions**: Select "Full Access" (or "Restricted Access" with Mail Send enabled)
6. **Click**: "Create & View"
7. **COPY THE API KEY** (you can only see it once!)

**Example API Key**:
```
SG.xxxxxxxxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
```

⚠️ **Save this key somewhere safe!** You won't see it again.

---

### Step 3: Verify Sender Identity

SendGrid requires you to verify your email address before sending:

1. **Navigate to**: Settings → Sender Authentication
2. **Choose Option**:
   - **Option A (Easiest)**: Single Sender Verification
     - Click "Get Started"
     - Enter your email: `dev.nexonx@gmail.com`
     - Fill in name and address
     - Click "Create"
     - **Check your email** and click verification link
   
   - **Option B (Professional)**: Domain Authentication (if you have a domain)
     - Verify your entire domain
     - Requires DNS changes

**For testing, use Option A** (Single Sender Verification)

---

### Step 4: Add Environment Variables to Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Select service**: `expense-tracker-api`
3. **Click**: "Environment" tab
4. **Add these variables**:

| Key | Value | Example |
|-----|-------|---------|
| `SENDGRID_API_KEY` | Your SendGrid API key | `SG.xxxxxxx.yyyyyyy` |
| `FROM_EMAIL` | Your verified email | `dev.nexonx@gmail.com` |
| `FRONTEND_URL` | Your frontend URL | `https://expense-fe-chi.vercel.app` |

5. **Click**: "Save Changes"

Render will automatically restart your service (~30 seconds).

---

### Step 5: Test Email Sending

After the service restarts, test registration:

```bash
curl -X POST https://your-api.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

**Check Render logs** for:
```
✅ OTP email sent successfully to test@example.com
```

**Check your email inbox** for the OTP!

---

## 📊 How It Works

### Before (SMTP - Blocked):
```
FastAPI → SMTP (port 587) → ❌ Network Unreachable
```

### After (SendGrid API - Works):
```
FastAPI → SendGrid API (HTTPS) → ✅ Email Delivered
```

SendGrid uses HTTPS (port 443) which is never blocked!

---

## ✅ Verify Setup

### 1. Check Environment Variables

In Render Dashboard → Environment, verify:
- ✅ `SENDGRID_API_KEY` is set (starts with `SG.`)
- ✅ `FROM_EMAIL` matches your verified email
- ✅ `FRONTEND_URL` is correct

### 2. Check SendGrid Dashboard

After testing, check SendGrid Dashboard → Activity:
- You should see successful email deliveries
- Shows sent count, delivery rate, open rate

### 3. Check Render Logs

Look for:
```
✅ OTP email sent successfully to user@example.com
```

NOT:
```
[DEV MODE] OTP for user@example.com: 123456
```

---

## 🎨 Email Features

The new SendGrid implementation includes:
- ✅ Beautiful HTML emails (styled)
- ✅ Responsive design
- ✅ Professional templates
- ✅ Better deliverability
- ✅ Email tracking (via SendGrid dashboard)

**Example OTP Email:**
```
┌─────────────────────────────┐
│   Email Verification         │
├─────────────────────────────┤
│ Hi John,                     │
│                              │
│ Your OTP code is:            │
│                              │
│    ┌───────────┐             │
│    │  123456   │             │
│    └───────────┘             │
│                              │
│ Expires in 10 minutes        │
└─────────────────────────────┘
```

---

## 🚨 Troubleshooting

### Issue: "Unauthorized" Error

**Cause**: Invalid or expired API key

**Fix**:
1. Generate new API key in SendGrid
2. Update `SENDGRID_API_KEY` in Render
3. Save and restart

### Issue: "Forbidden" Error

**Cause**: Sender email not verified

**Fix**:
1. Go to SendGrid → Sender Authentication
2. Verify your email address
3. Check email for verification link
4. Click verify

### Issue: Emails Not Received

**Check**:
1. ✅ Spam/Junk folder
2. ✅ SendGrid Activity tab (was it sent?)
3. ✅ Email address correct
4. ✅ SendGrid free tier limit (100/day)

### Issue: Still Shows "[DEV MODE]"

**Cause**: `SENDGRID_API_KEY` not set

**Fix**:
1. Verify environment variable in Render
2. Check for typos in variable name
3. Restart service after adding

---

## 📈 SendGrid Free Tier Limits

| Feature | Limit |
|---------|-------|
| Emails/day | 100 |
| Emails/month | 3,000 |
| Validity | Forever |
| API Calls | Unlimited |
| Sender Verification | 10 senders |

**Perfect for:**
- ✅ Testing and development
- ✅ Small production apps
- ✅ Up to 50 users registering per day

**If you need more**: Upgrade to paid plan later

---

## 🔐 Security Best Practices

1. **Never commit API keys** to git
2. **Use environment variables** only
3. **Restrict API key permissions** (Mail Send only)
4. **Rotate keys** periodically
5. **Monitor usage** in SendGrid dashboard

---

## 📞 Summary

**Problem**: Render blocks SMTP → emails not sent  
**Solution**: Use SendGrid API  
**Time**: 5 minutes setup  
**Cost**: FREE (100 emails/day)  
**Result**: Reliable email delivery on Render  

**Next Steps**:
1. ✅ Create SendGrid account
2. ✅ Get API key
3. ✅ Verify sender email
4. ✅ Add to Render environment variables
5. ✅ Test registration
6. ✅ Receive emails!

---

## 🎉 Alternative Services

If you prefer other services:

| Service | Free Tier | Setup Complexity |
|---------|-----------|------------------|
| **SendGrid** | 100/day | ⭐ Easy |
| Mailgun | 100/day | ⭐⭐ Medium |
| AWS SES | 62,000/month | ⭐⭐⭐ Complex |
| Postmark | 100/month | ⭐⭐ Medium |
| Resend | 100/day | ⭐ Easy |

**Recommendation**: Start with SendGrid!

---

Good luck! 🚀

