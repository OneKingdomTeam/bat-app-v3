# Coach Notification Feature - Deployment Guide

## Overview
This deployment adds a "Notify Coach" button to the assessment edit page that allows users to send email notifications to their assigned coach when they've completed their assessment.

## Key Features
- **Coach Assignment**: Required coach assignment during assessment creation (admin/coach roles only)
- **Email Notification**: Users can notify their coach with a single click
- **Rate Limiting**: One notification per 30 minutes per assessment to prevent spam
- **SMTP Check**: Button automatically hidden if SMTP is not configured
- **Security**: Backend validation of coach role and user permissions

## Database Migration

### Step 1: Backup Your Database
Before running any migration, create a backup of your database:
```bash
cp /path/to/database.db /path/to/database.db.backup
```

### Step 2: Run the Migration
Execute the SQL migration script on your production database:

```bash
sqlite3 /path/to/database.db < migration_add_coach_notification.sql
```

Or manually run these SQL commands:
```sql
ALTER TABLE assessments ADD COLUMN coach_id TEXT REFERENCES users(user_id);
ALTER TABLE assessments ADD COLUMN last_notification_sent TEXT;
```

### Step 3: Verify Migration
Check that the columns were added successfully:
```sql
PRAGMA table_info(assessments);
```

You should see `coach_id` and `last_notification_sent` in the output.

## Deployment Steps

### 1. Deploy Code
Deploy the updated codebase to your production environment:
```bash
git pull origin main
# or
git pull origin feature/notify-coach-button
```

### 2. Restart Application
Restart your application server to load the new code:
```bash
# Example for systemd service
sudo systemctl restart bat-app

# Or if using Docker
docker-compose restart
```

### 3. Verify SMTP Configuration
Ensure SMTP is configured for email notifications to work. Check your environment variables:
```bash
echo $SMTP_LOGIN
echo $SMTP_SERVER
echo $SMTP_PORT
echo $SMTP_EMAIL
```

All SMTP variables must be set for the feature to be enabled.

## Handling Existing Assessments

### Option 1: Leave Coach Field Empty
Existing assessments without a coach will simply not show the "Notify Coach" button. This is the safest option.

### Option 2: Assign Default Coach
If you want existing assessments to have the notification feature, assign a default coach:

```sql
-- Assign the first admin as default coach for all existing assessments
UPDATE assessments
SET coach_id = (SELECT user_id FROM users WHERE role = 'admin' LIMIT 1)
WHERE coach_id IS NULL;
```

Or assign different coaches based on the owner:
```sql
-- Example: Assign coach based on ownership or other criteria
UPDATE assessments
SET coach_id = (SELECT user_id FROM users WHERE role = 'coach' AND username = 'john_coach')
WHERE owner_id IN (SELECT user_id FROM users WHERE username IN ('user1', 'user2'));
```

## Testing Checklist

After deployment, verify the following:

### 1. Assessment Creation
- [ ] Navigate to `/dashboard/assessments/create`
- [ ] Verify that "Coach" dropdown only shows admin and coach users
- [ ] Verify that "Owner" dropdown also shows admin and coach users
- [ ] Create a new assessment with a coach assigned
- [ ] Verify assessment is created successfully

### 2. Coach Assignment Validation
- [ ] Try to create an assessment (use browser dev tools to manually set coach_id to a regular user)
- [ ] Verify that backend rejects invalid coach assignment with error message

### 3. Notify Coach Button
- [ ] Login as a regular user
- [ ] Navigate to `/app/assessments/edit/{assessment_id}` for an assessment with a coach
- [ ] Verify "Notify Coach" button appears below "Let's do it!" button
- [ ] Verify button has warning color (yellow) and help text

### 4. Email Notification
- [ ] Click "Notify Coach" button
- [ ] Verify success message appears: "Notification sent successfully to your coach!"
- [ ] Check coach's email inbox for notification email
- [ ] Verify email contains:
  - Coach's name in greeting
  - User's name who sent notification
  - Assessment name
  - Direct link to dashboard review page
  - Organization branding

### 5. Rate Limiting
- [ ] Click "Notify Coach" button again within 30 minutes
- [ ] Verify info message appears about 30-minute cooldown
- [ ] Message should encourage direct contact with coach
- [ ] Wait 30 minutes and verify button works again

### 6. SMTP Not Configured
- [ ] Temporarily unset SMTP environment variables
- [ ] Restart application
- [ ] Navigate to assessment edit page
- [ ] Verify "Notify Coach" button is hidden
- [ ] Restore SMTP configuration

### 7. No Coach Assigned
- [ ] View an existing assessment without a coach (from before migration)
- [ ] Verify "Notify Coach" button is hidden
- [ ] Verify no errors occur

### 8. Permissions
- [ ] Verify only assessment owners and collaborators can send notifications
- [ ] Verify coach receives notification even if they're not the owner

## Troubleshooting

### Button Not Appearing
**Possible Causes:**
1. SMTP not configured - Check environment variables
2. No coach assigned to assessment - Assign a coach via database update or recreate assessment
3. Template not updated - Clear any template caches and restart application

### Email Not Sending
**Possible Causes:**
1. SMTP credentials incorrect - Test SMTP configuration
2. Coach email address invalid - Check user's email in database
3. Firewall blocking SMTP port - Check network connectivity

**Check Logs:**
```bash
# View application logs for email errors
tail -f /path/to/application.log | grep -i "email\|smtp"
```

### Rate Limiting Not Working
**Possible Causes:**
1. Database column not added - Verify migration ran successfully
2. Timestamp parsing issue - Check `last_notification_sent` format in database

**Debug:**
```sql
-- Check notification timestamps
SELECT assessment_id, assessment_name, last_notification_sent
FROM assessments
WHERE last_notification_sent IS NOT NULL;
```

### Coach Dropdown Empty
**Possible Causes:**
1. No users with admin or coach role - Create admin/coach users
2. Permission issue - Verify current user has `can_manage_assessments()` permission

**Check Users:**
```sql
-- List all admins and coaches
SELECT user_id, username, email, role FROM users WHERE role IN ('admin', 'coach');
```

## Rollback Plan

If you need to rollback this feature:

### 1. Rollback Code
```bash
git revert <commit-hash>
# or
git checkout <previous-version>
```

### 2. Restart Application
```bash
sudo systemctl restart bat-app
```

### 3. (Optional) Remove Database Columns
**Warning:** Only do this if you need to completely remove the feature. Data will be lost.

```sql
-- SQLite doesn't support DROP COLUMN directly, need to recreate table
-- Only run this if absolutely necessary
-- BACKUP YOUR DATABASE FIRST!

-- This is complex in SQLite - consider keeping the columns as they're harmless
```

## Security Considerations

✅ **Implemented Security Measures:**
- Backend validation of coach role (admin/coach only)
- Authorization check: only owners/collaborators can send notifications
- Rate limiting prevents spam (30-minute cooldown)
- SMTP check prevents errors when email not configured
- No coach information exposed to unauthorized users

⚠️ **Important Notes:**
- Coach email addresses are visible to users in notification context
- Notification timestamps stored in plain text format
- Frontend validation is a helper; backend validation is the security boundary

## Support

For issues or questions:
1. Check application logs: `/path/to/application.log`
2. Check database consistency: Run verification queries above
3. Review this deployment guide thoroughly
4. Contact development team if issues persist

---

**Deployment Completed:** [Date]
**Deployed By:** [Name]
**Version:** 3.0.12 (or appropriate version number)
