# Deploy Migrations Without Shell Access

Since Shell access requires a paid plan on Render, we've configured automatic migrations during deployment.

## ✅ Solution Applied

Updated `render.yaml` to run migrations automatically:

```yaml
buildCommand: "pip install -r requirements.txt && alembic upgrade head"
```

This will:
1. Install dependencies
2. Automatically run database migrations
3. Start the server

## 🚀 Deploy Now

Run these commands to trigger the deployment:

```bash
cd /home/vishal/Downloads/temp_BE

# Add the updated render.yaml
git add render.yaml

# Commit the change
git commit -m "fix: Auto-run migrations during build on Render"

# Push to trigger deployment
git push origin main
```

## 📊 What Happens Next

1. **Render detects the push** and starts building
2. **Install dependencies** (`pip install -r requirements.txt`)
3. **Run migrations** (`alembic upgrade head`) ✨ This fixes the error!
4. **Start the server** (`uvicorn app.main:app ...`)

## 🔍 Monitor Deployment

1. Go to Render Dashboard: https://dashboard.render.com
2. Select **expense-tracker-api**
3. Watch the **Logs** tab to see:
   - Dependencies installing
   - Migrations running
   - Server starting

**Look for these lines in the logs:**
```
INFO  [alembic.runtime.migration] Running upgrade -> 43933116c651
INFO  [alembic.runtime.migration] Running upgrade 43933116c651 -> 74f7ca8b76b3
✅ Migrations completed!
```

## ⏱️ Timeline

- **Build time**: ~2-3 minutes
- **Migration time**: ~5-10 seconds
- **Total**: ~3 minutes

## ✅ After Deployment

Once deployment completes:

1. **Test the registration endpoint**:
```bash
curl -X POST https://expense-tracker-api.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

2. **Expected response** (Success!):
```json
{
  "message": "Registration successful! Please check your email for OTP verification code.",
  "user_id": "uuid-here",
  "email": "test@example.com",
  "email_verified": false
}
```

3. **Check logs for OTP** (since SMTP might not be configured):
   - Go to Render Dashboard → Logs
   - Look for: `[DEV MODE] OTP for test@example.com: 123456`

## 🔐 Existing Users

After migration, existing users will have `email_verified = false`. 

**To allow them to login**, you have two options:

### Option 1: Manual SQL Update (One-time)

Contact Render support or use a database client to run:
```sql
UPDATE users SET email_verified = true 
WHERE created_at < NOW() - INTERVAL '1 day';
```

### Option 2: Temporary Fix in Code

Add this to `app/routers/auth.py` login function temporarily:

```python
# Temporary: Auto-verify old users
if not user.email_verified and user.created_at < datetime.utcnow() - timedelta(days=1):
    user.email_verified = True
    db.commit()
```

Then remove it after all existing users have logged in once.

## 🚨 Troubleshooting

### If build fails:

**Check Render logs for errors like:**
- `alembic: command not found` → Means alembic not installed (shouldn't happen)
- `No such revision` → Migration file not committed to git
- `Can't locate revision` → Need to stamp database first

**Fix:**
```bash
# Make sure all migration files are committed
git add alembic/versions/*.py
git commit -m "Add migration files"
git push origin main
```

### If migrations run but still get error:

Check that these files are in your git repo:
- `alembic/versions/43933116c651_add_email_verified_field_to_users.py`
- `alembic/versions/74f7ca8b76b3_add_friend_invitations_table.py`
- `app/models/invitation.py`

```bash
# Verify files are tracked
git ls-files | grep -E "(migration|invitation)"
```

## 📋 Deployment Checklist

Before pushing:
- [x] Updated `render.yaml` with migration command
- [ ] Committed all new files (models, migrations, services)
- [ ] Pushed to GitHub
- [ ] Monitored Render deployment logs
- [ ] Verified migrations ran successfully
- [ ] Tested registration endpoint
- [ ] Checked for OTP in logs

## 🎯 Summary

**Problem**: Can't access shell on free tier  
**Solution**: Auto-run migrations during build  
**Action Required**: Push updated `render.yaml`  
**Result**: Migrations run automatically on every deployment  

This is actually a **better solution** than manual shell access because:
- ✅ Migrations run automatically
- ✅ No manual intervention needed
- ✅ Works on every deployment
- ✅ Consistent and reliable

---

Ready to deploy? Run the git commands above! 🚀

