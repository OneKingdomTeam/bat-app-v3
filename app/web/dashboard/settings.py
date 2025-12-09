from fastapi import APIRouter, Request, UploadFile, File, Form, Depends
from fastapi.responses import HTMLResponse
from pathlib import Path

from app.model.user import User
from app.model.notification import Notification
from app.model.setting import BrandingSettings
from app.template.init import jinja
from app.service.authentication import admin_only
from app.service import setting as service
from app.config import (
    ALLOWED_LOGO_EXTENSIONS,
    ALLOWED_FAVICON_EXTENSIONS,
    MAX_LOGO_SIZE,
    MAX_FAVICON_SIZE,
    IMAGES_DIR,
)

router = APIRouter()


# -------------------------------------
# Settings Page
# -------------------------------------


@router.get("", response_class=HTMLResponse, name="dashboard_settings_page")
def get_settings_page(request: Request, current_user: User = Depends(admin_only)):
    """Main settings page."""

    branding = service.get_branding_settings()

    context = {
        "request": request,
        "title": "Settings",
        "description": "Instance configuration and branding settings.",
        "current_user": current_user,
        "branding": branding,
    }

    return jinja.TemplateResponse(name="dashboard/settings.html", context=context)


# -------------------------------------
# Branding Settings
# -------------------------------------


@router.get(
    "/branding", response_class=HTMLResponse, name="dashboard_settings_branding"
)
def get_branding_settings_partial(
    request: Request, current_user: User = Depends(admin_only)
):
    """Get branding settings partial for HTMX."""

    branding = service.get_branding_settings()

    context = {
        "request": request,
        "branding": branding,
    }

    return jinja.TemplateResponse(
        name="dashboard/settings-branding.html", context=context
    )


@router.post("/branding", response_class=HTMLResponse)
async def update_branding_settings(
    request: Request,
    current_user: User = Depends(admin_only),
    feedback_url: str = Form(...),
    feedback_button_text: str = Form(...),
    organization_name: str = Form(...),
    organization_url: str = Form(...),
):
    """Update branding settings (text fields only)."""

    try:
        # Get current branding to preserve logo/favicon if not uploading new ones
        current_branding = service.get_branding_settings()

        # Validate inputs
        if not feedback_url.strip():
            raise ValueError("Feedback URL cannot be empty")
        if not feedback_button_text.strip():
            raise ValueError("Feedback button text cannot be empty")
        if not organization_name.strip():
            raise ValueError("Organization name cannot be empty")
        if not organization_url.strip():
            raise ValueError("Organization URL cannot be empty")

        updated_branding = BrandingSettings(
            logo_filename=current_branding.logo_filename,
            favicon_filename=current_branding.favicon_filename,
            feedback_url=feedback_url.strip(),
            feedback_button_text=feedback_button_text.strip(),
            organization_name=organization_name.strip(),
            organization_url=organization_url.strip(),
        )

        service.update_branding_settings(updated_branding)

        notification = Notification(
            style="success", content="Branding settings updated successfully"
        )

    except ValueError as e:
        notification = Notification(style="warning", content=str(e))
        updated_branding = service.get_branding_settings()
    except Exception as e:
        notification = Notification(
            style="danger", content=f"Failed to update settings: {str(e)}"
        )
        updated_branding = service.get_branding_settings()

    context = {
        "request": request,
        "branding": updated_branding,
        "notification": notification,
    }

    response = jinja.TemplateResponse(
        name="dashboard/settings-branding.html", context=context
    )

    # Trigger a page reload to update branding in header/footer
    if notification.style == "success":
        response.headers["HX-Refresh"] = "true"

    return response


@router.post("/branding/logo", response_class=HTMLResponse)
async def upload_logo(
    request: Request,
    current_user: User = Depends(admin_only),
    logo_file: UploadFile = File(...),
):
    """Upload a new logo file."""

    branding = service.get_branding_settings()
    notification = None

    try:
        # Validate file was provided
        if not logo_file.filename:
            raise ValueError("No file selected")

        # Validate file extension
        file_ext = Path(logo_file.filename).suffix.lower()
        if file_ext not in ALLOWED_LOGO_EXTENSIONS:
            raise ValueError(
                f"Invalid file type '{file_ext}'. Allowed formats: PNG, JPG, WebP, SVG"
            )

        # Read file content
        content = await logo_file.read()

        # Validate file size
        file_size = len(content)
        if file_size == 0:
            raise ValueError("File is empty")
        if file_size > MAX_LOGO_SIZE:
            size_kb = file_size / 1024
            max_kb = MAX_LOGO_SIZE / 1024
            raise ValueError(
                f"File too large ({size_kb:.1f} KB). Maximum size: {max_kb:.0f} KB"
            )

        # Ensure images directory exists
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)

        # Generate safe filename
        safe_filename = f"custom-logo{file_ext}"
        file_path = IMAGES_DIR / safe_filename

        # Save file
        with open(file_path, "wb") as f:
            f.write(content)

        # Update setting
        service.set_setting(service.BRANDING_LOGO, safe_filename)

        # Reload branding to get updated filename
        branding = service.get_branding_settings()

        notification = Notification(
            style="success",
            content=f"Logo uploaded successfully ({file_size / 1024:.1f} KB)",
        )

    except ValueError as e:
        notification = Notification(style="warning", content=str(e))
    except PermissionError:
        notification = Notification(
            style="danger",
            content="Failed to save file: Permission denied. Check directory permissions.",
        )
    except OSError as e:
        notification = Notification(
            style="danger", content=f"Failed to save file: {str(e)}"
        )
    except Exception as e:
        notification = Notification(
            style="danger", content=f"Unexpected error: {str(e)}"
        )

    context = {
        "request": request,
        "branding": branding,
        "notification": notification,
    }

    response = jinja.TemplateResponse(
        name="dashboard/settings-branding.html", context=context
    )

    # Trigger page reload to show new logo only on success
    if notification and notification.style == "success":
        response.headers["HX-Refresh"] = "true"

    return response


@router.post("/branding/favicon", response_class=HTMLResponse)
async def upload_favicon(
    request: Request,
    current_user: User = Depends(admin_only),
    favicon_file: UploadFile = File(...),
):
    """Upload a new favicon file."""

    branding = service.get_branding_settings()
    notification = None

    try:
        # Validate file was provided
        if not favicon_file.filename:
            raise ValueError("No file selected")

        # Validate file extension
        file_ext = Path(favicon_file.filename).suffix.lower()
        if file_ext not in ALLOWED_FAVICON_EXTENSIONS:
            raise ValueError(
                f"Invalid file type '{file_ext}'. Allowed formats: PNG, JPG, WebP, ICO"
            )

        # Read file content
        content = await favicon_file.read()

        # Validate file size
        file_size = len(content)
        if file_size == 0:
            raise ValueError("File is empty")
        if file_size > MAX_FAVICON_SIZE:
            size_kb = file_size / 1024
            max_kb = MAX_FAVICON_SIZE / 1024
            raise ValueError(
                f"File too large ({size_kb:.1f} KB). Maximum size: {max_kb:.0f} KB"
            )

        # Ensure images directory exists
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)

        # Generate safe filename
        safe_filename = f"custom-favicon{file_ext}"
        file_path = IMAGES_DIR / safe_filename

        # Save file
        with open(file_path, "wb") as f:
            f.write(content)

        # Update setting
        service.set_setting(service.BRANDING_FAVICON, safe_filename)

        # Reload branding to get updated filename
        branding = service.get_branding_settings()

        notification = Notification(
            style="success",
            content=f"Favicon uploaded successfully ({file_size / 1024:.1f} KB)",
        )

    except ValueError as e:
        notification = Notification(style="warning", content=str(e))
    except PermissionError:
        notification = Notification(
            style="danger",
            content="Failed to save file: Permission denied. Check directory permissions.",
        )
    except OSError as e:
        notification = Notification(
            style="danger", content=f"Failed to save file: {str(e)}"
        )
    except Exception as e:
        notification = Notification(
            style="danger", content=f"Unexpected error: {str(e)}"
        )

    context = {
        "request": request,
        "branding": branding,
        "notification": notification,
    }

    response = jinja.TemplateResponse(
        name="dashboard/settings-branding.html", context=context
    )

    # Trigger page reload to show new favicon only on success
    if notification and notification.style == "success":
        response.headers["HX-Refresh"] = "true"

    return response
