# Branding Customization Guide

## Overview

The BAT App now supports **database-driven branding customization**, perfect for containerized deployments. Administrators can customize logos, favicons, and footer links directly through the web interface without modifying files or environment variables.

## Features

### What Can Be Customized

1. **Logo** - Main logo displayed in navbar and footers
2. **Favicon** - Browser tab icon
3. **Feedback URL** - Link for feedback form (dashboard footer)
4. **Feedback Button Text** - Customizable button label
5. **Team/Company Name** - Your organization name
6. **Team/Company URL** - Link to your organization's website

### Key Benefits

- ✅ **Container-friendly**: No file mounting required
- ✅ **Database-stored**: Persists across container restarts
- ✅ **Web-based UI**: Easy configuration through admin settings page
- ✅ **File uploads**: Upload custom logos and favicons directly
- ✅ **Immediate effect**: Changes apply instantly with page refresh
- ✅ **Admin-only**: Protected by role-based access control

## How to Customize Branding

### Step 1: Access Settings Page

1. Log in as an **admin** user
2. Navigate to the dashboard
3. Click **"Settings"** in the navigation menu (admin-only link)
4. The Settings page will open with the Branding section

### Step 2: Upload Custom Images

#### Upload Logo
- Click **"Choose logo…"** button
- Select your logo file (PNG, JPG, WebP, or SVG)
- Click **"Upload"**
- **Recommended dimensions**: 300x66 pixels (landscape orientation, ~4.5:1 aspect ratio)
- Your logo will be saved as `custom-logo.[ext]` in the images directory
- Page will refresh automatically to show the new logo

#### Upload Favicon
- Click **"Choose favicon…"** button
- Select your favicon file (PNG, WebP, or ICO)
- Click **"Upload"**
- **Recommended dimensions**: 32x32 or 64x64 pixels
- Your favicon will be saved as `custom-favicon.[ext]` in the images directory
- Page will refresh automatically to show the new favicon

### Step 3: Configure Text Settings

Fill in or modify the following fields:

1. **Feedback Form URL**
   - Enter the full URL to your feedback form
   - Supports Google Forms, Typeform, Monday.com, or any custom form
   - Example: `https://forms.google.com/your-form-id`

2. **Feedback Button Text**
   - Customize the button label (e.g., "Send Feedback", "Contact Us")
   - Default: "Give us Feedback"

3. **Team/Company Name**
   - Your organization's name
   - Appears in footers and "Developed by..." text
   - Example: "Acme Corporation"

4. **Team/Company URL**
   - Full URL to your organization's website
   - Example: `https://www.acme-corp.com/`

5. Click **"Save Branding Settings"** to apply changes

## Technical Details

### Database Structure

Branding settings are stored in the `settings` table with a key-value structure:

```sql
CREATE TABLE settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT
)
```

Branding keys use the prefix `branding.*`:
- `branding.logo_filename`
- `branding.favicon_filename`
- `branding.feedback_url`
- `branding.feedback_button_text`
- `branding.team_name`
- `branding.team_url`

### File Storage

Uploaded files are stored in: `app/static/images/`

**Naming convention:**
- Logo: `custom-logo.[extension]`
- Favicon: `custom-favicon.[extension]`

Files are persisted in the container's `/app/static/images/` directory, which should be part of your persistent volume strategy if you want uploads to survive container rebuilds.

### Default Values

On first startup, the system initializes with OneKingdom Team branding:

```python
{
    "logo_filename": "bat-logo-300x66.png",
    "favicon_filename": "bat-favicon.webp",
    "feedback_url": "https://forms.monday.com/forms/ec025da1e8378bc7535f1522af9647e6?r=use1",
    "feedback_button_text": "Give us Feedback",
    "team_name": "OneKingdom Team",
    "team_url": "https://onekingdom.team/",
}
```

## Architecture

### New Files Created

1. **Models** (`app/model/setting.py`)
   - `InstanceSetting` - Base key-value model
   - `BrandingSettings` - Typed branding configuration

2. **Data Layer** (`app/data/setting.py`)
   - Database CRUD operations
   - SQLite table creation and management

3. **Service Layer** (`app/service/setting.py`)
   - Business logic for branding settings
   - Default initialization
   - Helper functions for get/set operations

4. **Web Routes** (`app/web/dashboard/settings.py`)
   - Admin-only settings page
   - Branding configuration endpoints
   - File upload handling

5. **Templates**
   - `app/template/jinja/dashboard/settings.html` - Main settings page
   - `app/template/jinja/dashboard/settings-branding.html` - Branding section

### Modified Files

1. **Template Context** (`app/template/init.py`)
   - Added `get_branding()` global function for templates
   - Dynamic branding injection with fallback to defaults

2. **Footers**
   - `app/template/jinja/footer.html` - Uses dynamic branding
   - `app/template/jinja/dashboard/footer.html` - Uses dynamic feedback URL and team info

3. **Base Template** (`app/template/jinja/index.html`)
   - Dynamic favicon and logo references

4. **Navigation** (`app/template/jinja/dashboard/menu.html`)
   - Added "Settings" link (admin-only)

5. **Application Startup** (`app/main.py`)
   - Calls `add_default_settings()` on startup
   - Registers settings router

## Logo Guidelines

### Main Logo (Navbar/Footer)

**Optimal Specifications:**
- **Dimensions**: 300x66 pixels
- **Aspect Ratio**: ~4.5:1 (landscape orientation)
- **Format**: PNG (preferred), JPG, WebP, or SVG
- **Background**: Transparent or white
- **File Size**: Keep under 100KB for performance
- **Content**: Should be legible at small sizes

**Design Tips:**
- Use horizontal wordmark or logo + text combination
- Ensure good contrast against light backgrounds
- Test visibility at small sizes (navbar collapses on mobile)
- Avoid fine details that don't scale well

### Favicon

**Optimal Specifications:**
- **Dimensions**: 32x32 or 64x64 pixels (square)
- **Format**: PNG, WebP, or ICO
- **Background**: Can be transparent or solid
- **File Size**: Keep under 10KB
- **Content**: Simple icon or lettermark

**Design Tips:**
- Use bold, simple shapes
- High contrast for visibility
- Recognizable at tiny sizes
- Consider using your logo's icon element

## Access Control

The Settings page is **admin-only**:
- Only users with `role = "admin"` can access `/dashboard/settings`
- The Settings link in navigation only appears for admins
- Attempting to access settings as non-admin returns `401 Unauthorized`

**To create an admin user:**
```bash
# Default admin credentials (configured in .env):
Username: admin
Email: admin@example.com
Password: password123456

# Change these immediately after first login!
```

## Troubleshooting

### Branding Not Appearing

**Issue**: After uploading, changes don't appear
**Solution**:
- Ensure you're using an admin account
- Hard refresh browser (Ctrl+Shift+R / Cmd+Shift+R)
- Check browser console for 404 errors
- Verify files were uploaded to `app/static/images/`

### Upload Fails

**Issue**: File upload returns error
**Solution**:
- Check file format (PNG, JPG, WebP, SVG for logo; PNG, WebP, ICO for favicon)
- Ensure file size is reasonable (< 5MB)
- Verify write permissions on `app/static/images/` directory
- Check application logs for detailed error messages

### Settings Page Not Accessible

**Issue**: Settings link not visible or 401 error
**Solution**:
- Ensure you're logged in as admin (not coach or user)
- Check user role: `SELECT username, role FROM users;`
- Promote user to admin: `UPDATE users SET role='admin' WHERE username='youruser';`

### Database Errors on Startup

**Issue**: Application fails to start with settings table errors
**Solution**:
- Ensure database file has write permissions
- Check disk space in persistent volume
- Review startup logs for SQLite errors
- If corrupted, remove database and restart (data loss!)

## Future Expansion

The settings infrastructure is designed to support additional configuration options:

### Planned Settings Categories

1. **SMTP Configuration** (future)
   - Email server settings via UI instead of environment variables

2. **Cloudflare Turnstile** (future)
   - CAPTCHA configuration through settings page

3. **Appearance Settings** (future)
   - Custom color schemes
   - Theme selection

4. **Security Settings** (future)
   - Password policies
   - Session timeout configuration

### Extending the System

To add new settings categories:

1. Define models in `app/model/setting.py`
2. Add service layer functions in `app/service/setting.py`
3. Create routes in `app/web/dashboard/settings.py`
4. Add template section in `app/template/jinja/dashboard/settings.html`
5. Update initialization in `app/service/setting.py`

## Support

For issues or feature requests related to branding customization, please:

1. Check this documentation first
2. Review application logs for errors
3. Ensure you're using the latest version
4. Open an issue on the project repository with:
   - Steps to reproduce
   - Error messages
   - Browser and version
   - Admin user confirmation

## Summary

The new branding system provides a **production-ready, container-friendly solution** for customizing your BAT App instance. With database storage and a user-friendly web interface, administrators can easily white-label their deployment without touching configuration files or requiring container rebuilds.

**Key Takeaway**: Branding is now managed through the **Settings page** (admin-only), accessible via the dashboard navigation.
