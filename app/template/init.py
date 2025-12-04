
from fastapi.templating import Jinja2Templates
from pathlib import Path


root_dir = Path(__file__).resolve().parent
template_dir = root_dir / "jinja"


jinja = Jinja2Templates(directory=str(template_dir))


# Add branding context processor
def get_branding_context():
    """Get branding settings for template context."""
    try:
        from app.service.setting import get_branding_settings
        branding = get_branding_settings()
        return branding.model_dump()
    except Exception as e:
        # Fallback to defaults if database not initialized yet
        print(f"Warning: Could not load branding settings: {e}")
        return {
            "logo_filename": "bat-logo-300x66.png",
            "favicon_filename": "bat-favicon.webp",
            "feedback_url": "https://forms.monday.com/forms/ec025da1e8378bc7535f1522af9647e6?r=use1",
            "feedback_button_text": "Give us Feedback",
            "organization_name": "OneKingdom Team",
            "organization_url": "https://onekingdom.team/",
        }


# Make branding available to all templates as a function that gets fresh data
jinja.env.globals['get_branding'] = get_branding_context
