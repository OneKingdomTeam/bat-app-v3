# BAT App v3

A flexible, modern assessment application built with FastAPI, freed from WordPress for easier development and deployment.

## Quick Start

Choose your deployment method:
- **[Railway.app](#railway-deployment)** - One-click cloud deployment (recommended)
- **[Local Development](#local-development)** - Run locally with FastAPI
- **[Container](#container-deployment)** - Docker/Podman compose

---

## Railway Deployment

### Setup

1. **Create Project**
   - Go to [Railway.app](https://railway.app) and login
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `bat-app-v3` repository

2. **Configure Environment Variables**

   Required:
   ```bash
   SECRET_KEY=<generate-with-openssl-rand-hex-32>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   DEFAULT_USER=admin
   DEFAULT_EMAIL=admin@example.com
   DEFAULT_PASSWORD=<your-secure-password>
   FORCE_HTTPS_PATHS=True
   ```

   Optional (email notifications):
   ```bash
   SMTP_LOGIN=your-smtp-username
   SMTP_PASSWORD=your-smtp-password
   SMTP_EMAIL=noreply@yourdomain.com
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```

   Optional (Cloudflare Turnstile CAPTCHA):
   ```bash
   CF_TURNSTILE_SITE_KEY=your-site-key
   CF_TURNSTILE_SECRET_KEY=your-secret-key
   ```

3. **Generate SECRET_KEY**
   ```bash
   openssl rand -hex 32
   ```

4. **Deploy** - Railway will automatically install dependencies and start the app

### Persistent Storage (CRITICAL)

Railway uses ephemeral storage by default. You **MUST** configure a volume to prevent data loss.

**Add Volume:**
1. Open Railway project → Settings → Volumes
2. Click "+ Add Volume"
3. Mount Path: `/bat-app/persistent`
4. Redeploy

This single volume contains:
- `persistent/db/` - SQLite database
- `persistent/uploads/` - User files and reports

**Without this volume, all data is lost on each deployment.**

### Troubleshooting

- **Data lost after redeploy:** Add persistent volume (see above)
- **Can't log in:** Check `DEFAULT_USER`/`DEFAULT_PASSWORD` in environment variables
- **App crashes:** Check Railway logs for errors
- **SMTP not working:** Verify all SMTP variables are set; use Gmail App Password

---

## Branding Customization

BAT App supports database-driven branding customization - perfect for white-labeling your deployment.

### What You Can Customize

- Logo (navbar/footer)
- Favicon (browser icon)
- Feedback form URL and button text
- Company name and website URL

### How to Customize

1. **Access Settings**
   - Log in as admin
   - Navigate to Dashboard → Settings

2. **Upload Images**
   - **Logo:** 300x66px recommended (PNG, JPG, WebP, SVG)
   - **Favicon:** 32x32 or 64x64px (PNG, WebP, ICO)

3. **Configure Text**
   - Set feedback form URL (Google Forms, Typeform, etc.)
   - Customize feedback button text
   - Add your company name and website

4. **Save** - Changes apply immediately

### Key Features

- Container-friendly (no file mounting needed)
- Database-stored (persists across restarts)
- Web-based UI (easy configuration)
- Admin-only access
- Immediate effect

All settings are stored in the database and managed through the admin Settings page. No environment variables or file editing required.

---

## Local Development

### Setup

1. **Generate SECRET_KEY**
   ```bash
   openssl rand -hex 32
   ```
   Add to `.env` file

2. **Initialize Database**
   ```bash
   export PYTHONPATH="$(pwd)"
   python -i app/main.py
   ```

   Then in Python:
   ```python
   from app.service.user import add_default_user
   from app.service.question import add_default_questions
   add_default_user()
   add_default_questions()
   ```

3. **Run Application**
   ```bash
   cd app
   fastapi run
   ```

### Environment Variables

Copy `.env.example` to `.env` and configure:
- `SECRET_KEY` (required)
- `DEFAULT_USER`, `DEFAULT_PASSWORD` (required)
- SMTP settings (optional)
- Cloudflare Turnstile keys (optional)

---

## Container Deployment

### Quick Start

```bash
# Build
podman build -f containerfile -t bat-app:latest .

# Run with compose
podman-compose up
# or
docker-compose up
```

### Volume Configuration

The `compose.yml` includes a persistent volume mount:

```yaml
volumes:
  - ./persistent:/bat-app/persistent:Z
```

Contains:
- `persistent/db/` - SQLite database
- `persistent/uploads/` - User files

The `:Z` flag is for SELinux systems (remove if not using SELinux).

Configure environment variables in `compose.yml` before running.

---

## Architecture

- **Framework:** FastAPI
- **Database:** SQLite (WAL mode)
- **Templates:** Jinja2
- **Authentication:** JWT tokens
- **File Storage:** Local filesystem
- **Branding:** Database-backed settings

## Features

- Multi-user support with role-based access (admin, coach, user)
- Assessment creation and management
- Report generation with visualizations
- Branding customization (logos, favicons, links)
- Email notifications (optional)
- CAPTCHA support (optional)
- Containerized deployment ready

## Support

Default admin credentials (change after first login):
- Username: `admin`
- Password: `password123456` (or value set in `DEFAULT_PASSWORD`)

For issues, check application logs and ensure all required environment variables are configured.
