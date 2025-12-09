# Coach Notification Feature - Changes Summary

## Files Modified

### 1. Models (`app/model/assesment.py`)
**Changes:**
- Added `coach_id`, `coach_name`, `last_notification_sent` fields to `Assessment` model
- Added `coach_id` field to `AssessmentPost` model (for form submission)
- Added `coach_id` field to `AssessmentNew` model (for creation)
- Created new `AssessmentNotifyCoach` model for notification requests

### 2. Data Layer (`app/data/assessment.py`)
**Changes:**
- Updated `assessments` table schema to include `coach_id` and `last_notification_sent` columns
- Modified `assessment_row_to_model()` to handle new coach fields
- Updated `create_assessment()` to accept and store `coach_id`
- Updated all SELECT queries to include coach information (LEFT JOIN with users table):
  - `get_one()`
  - `get_all_for_user()`
  - `get_one_for_user()`
  - `get_all()`
- Added `can_send_notification()` function for rate limiting checks
- Added `update_notification_timestamp()` function to update last notification time

### 3. Service Layer - Assessment (`app/service/assessment.py`)
**Changes:**
- Modified `create_assessment()` to:
  - Validate coach_id references admin/coach user
  - Pass coach_id to assessment creation
- Added `get_available_coaches_for_assessment()` to filter users by admin/coach role
- Added `notify_coach()` function to handle notification logic:
  - SMTP configuration check
  - User access verification
  - Coach assignment check
  - Rate limit check (30 minutes)
  - Email sending
  - Timestamp update

### 4. Service Layer - Mail (`app/service/mail.py`)
**Changes:**
- Added `notify_coach_assessment_complete()` function to send notification emails
- Creates dashboard review URL for coach access
- Uses `email/coach-notification.html` template

### 5. Exception Handling (`app/exception/service.py`)
**Changes:**
- Added `RateLimitExceeded` exception class
- Added `InvalidCoachAssignment` exception class

### 6. Dashboard Routes (`app/web/dashboard/assessments.py`)
**Changes:**
- Modified `get_assessment_create()` to:
  - Call `get_available_coaches_for_assessment()` instead of `get_all()`
  - Pass `coaches` instead of `users` to template
- Modified `post_assessment_create()` to:
  - Use filtered coaches list
  - Pass `coaches` to template on success and error

### 7. App Routes (`app/web/app/assessments.py`)
**Changes:**
- Modified `get_assessment_edit()` to:
  - Import and pass `SMTP_ENABLED` to template
  - Fetch full assessment object (not just QA)
  - Add assessment and SMTP_ENABLED to context
- Added `post_notify_coach()` endpoint at `/notify/{assessment_id}`:
  - Handles notification sending
  - Comprehensive exception handling
  - Returns updated assessment edit page with notification message

### 8. Dashboard Template (`app/template/jinja/dashboard/assessment-create.html`)
**Changes:**
- Renamed "Owner" dropdown to distinguish from new "Coach" dropdown
- Added "Coach" dropdown with:
  - Required field
  - Shows only admin/coach users
  - Displays role in parentheses
  - Help text
- Updated "Owner" dropdown with:
  - Required field
  - Shows coaches (admin/coach users)
  - Help text explaining purpose

### 9. App Template (`app/template/jinja/app/assessment-edit.html`)
**Changes:**
- Added notification include at top of page
- Added "Notify Coach" button:
  - Conditional display: `{% if SMTP_ENABLED and assessment.coach_id %}`
  - Warning button style (yellow)
  - HTMX POST to `/notify/{assessment_id}`
  - Help text below button

### 10. Email Template (NEW: `app/template/jinja/email/coach-notification.html`)
**New File:**
- Extends base email template
- Displays coach name, user name, assessment name
- Includes "Review Assessment" button with dashboard URL
- Fallback link for button
- Organization branding

### 11. Migration SQL (NEW: `migration_add_coach_notification.sql`)
**New File:**
- Adds `coach_id` column to assessments table
- Adds `last_notification_sent` column to assessments table
- Optional default coach assignment query
- Verification query

### 12. Deployment Guide (NEW: `DEPLOYMENT_COACH_NOTIFICATION.md`)
**New File:**
- Complete deployment instructions
- Database migration steps
- Testing checklist
- Troubleshooting guide
- Rollback plan
- Security considerations

## Database Schema Changes

```sql
-- Before
CREATE TABLE assessments(
    assessment_id TEXT PRIMARY KEY,
    assessment_name TEXT,
    owner_id TEXT REFERENCES users(user_id),
    last_edit TEXT,
    last_editor TEXT
);

-- After
CREATE TABLE assessments(
    assessment_id TEXT PRIMARY KEY,
    assessment_name TEXT,
    owner_id TEXT REFERENCES users(user_id),
    last_edit TEXT,
    last_editor TEXT,
    coach_id TEXT REFERENCES users(user_id),        -- NEW
    last_notification_sent TEXT                      -- NEW
);
```

## API Changes

### New Endpoint
- **POST** `/app/assessments/notify/{assessment_id}`
  - Sends email notification to assigned coach
  - Returns: Updated assessment edit page with notification
  - Exceptions:
    - `SMTPCredentialsNotSet` - SMTP not configured
    - `RateLimitExceeded` - Notification sent within last 30 minutes
    - `SendingEmailFailed` - Email sending failed
    - `Unauthorized` - User doesn't have access or no coach assigned

### Modified Endpoints
- **GET** `/dashboard/assessments/create`
  - Now returns only admin/coach users instead of all users
- **POST** `/dashboard/assessments/create`
  - Now requires `coach_id` in request body
  - Validates coach_id is admin/coach role
- **GET** `/app/assessments/edit/{assessment_id}`
  - Now includes `assessment` object and `SMTP_ENABLED` in context

## Feature Behavior

### Assessment Creation (Admin/Coach)
1. Navigate to assessment creation page
2. Select coach from dropdown (admin/coach roles only)
3. Select owner from dropdown (admin/coach users only)
4. Enter assessment name
5. Submit form
6. Backend validates coach role
7. Assessment created with assigned coach

### Notification Sending (User)
1. User navigates to their assessment edit page
2. If SMTP configured AND coach assigned: "Notify Coach" button appears
3. User clicks button
4. System checks:
   - User has access (owner or collaborator)
   - Coach is assigned
   - SMTP is enabled
   - Rate limit not exceeded (30 min cooldown)
5. Email sent to coach with:
   - Assessment name
   - User name
   - Direct link to dashboard review page
6. Notification timestamp updated
7. Success message displayed

### Rate Limiting
- One notification per 30 minutes per assessment
- Timer starts from last successful notification
- If user tries again too soon:
  - Info message displayed
  - Suggests contacting coach directly
  - No coach information revealed

### Backward Compatibility
- Existing assessments without coach: Button hidden
- Table schema change backward compatible (nullable columns)
- No breaking changes to existing API endpoints
- Graceful degradation when SMTP not configured

## Testing Coverage

✅ **Backend Validation:**
- Coach role validation (admin/coach only)
- User access verification (owner/collaborator)
- Rate limit enforcement
- SMTP configuration check

✅ **Frontend Behavior:**
- Button visibility based on conditions
- Proper HTMX integration
- Notification display
- Form validation

✅ **Email Functionality:**
- Template rendering
- URL generation (dashboard paths)
- SMTP sending
- Error handling

✅ **Security:**
- Authorization checks
- Role-based filtering
- Rate limiting
- No information leakage

## Dependencies

**No new external dependencies added.**

Existing dependencies used:
- `pydantic` - Model validation
- `fastapi` - Routing and endpoints
- `jinja2` - Template rendering
- `smtplib` - Email sending (built-in)
- `sqlite3` - Database (built-in)
- `babel` - Date formatting

## Configuration Requirements

**Required Environment Variables for Feature:**
```bash
SMTP_LOGIN=your_smtp_username
SMTP_PASSWORD=your_smtp_password
SMTP_EMAIL=noreply@yourcompany.com
SMTP_SERVER=smtp.yourprovider.com
SMTP_PORT=465
```

If any SMTP variable is missing, the feature gracefully degrades:
- Button is hidden
- No errors occur
- Other assessment functionality continues to work

## Performance Considerations

**Database Impact:**
- Two new columns added (minimal storage overhead)
- All assessment queries updated to include coach information (LEFT JOIN)
- No additional queries for rate limiting (uses existing assessment fetch)

**Email Impact:**
- Email sending is synchronous (blocks request)
- Consider async email sending for high-traffic deployments
- Rate limiting prevents email server overload

**Caching:**
- No caching implemented for coach list
- Consider caching if user list is large (100+ users)

## Future Enhancements

Potential improvements for future iterations:
1. Async email sending for better performance
2. Notification history/audit log
3. Customizable notification cooldown period
4. Multiple coaches per assessment
5. In-app notifications (not just email)
6. Email template customization by organization
7. Notification preferences for coaches
8. Batch notifications for multiple assessments

## Version Information

- **Feature Branch:** `feature/notify-coach-button`
- **Target Version:** 3.0.12 (or next version)
- **Merge Date:** [To be filled]
- **Migration Required:** Yes (database schema change)
