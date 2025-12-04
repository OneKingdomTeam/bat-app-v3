from pydantic import BaseModel
from typing import Optional


class InstanceSetting(BaseModel):
    """Model for instance-wide configuration settings stored in database."""
    setting_key: str
    setting_value: str | None


class BrandingSettings(BaseModel):
    """Model for branding-related settings that can be configured by admins."""
    logo_filename: Optional[str] = "bat-logo-300x66.png"
    favicon_filename: Optional[str] = "bat-favicon.webp"
    feedback_url: Optional[str] = "https://forms.monday.com/forms/ec025da1e8378bc7535f1522af9647e6?r=use1"
    feedback_button_text: Optional[str] = "Give us Feedback"
    organization_name: Optional[str] = "OneKingdom Team"
    organization_url: Optional[str] = "https://onekingdom.team/"
