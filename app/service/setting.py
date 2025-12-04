from app.data import setting as data
from app.model.setting import InstanceSetting, BrandingSettings
from app.exception.database import RecordNotFound


# Branding setting keys
BRANDING_LOGO = "branding.logo_filename"
BRANDING_FAVICON = "branding.favicon_filename"
BRANDING_FEEDBACK_URL = "branding.feedback_url"
BRANDING_FEEDBACK_TEXT = "branding.feedback_button_text"
BRANDING_ORGANIZATION_NAME = "branding.organization_name"
BRANDING_ORGANIZATION_URL = "branding.organization_url"


def add_default_settings():
    """Initialize default branding settings if they don't exist."""
    defaults = {
        BRANDING_LOGO: "bat-logo-300x66.png",
        BRANDING_FAVICON: "bat-favicon.webp",
        BRANDING_FEEDBACK_URL: "https://forms.monday.com/forms/ec025da1e8378bc7535f1522af9647e6?r=use1",
        BRANDING_FEEDBACK_TEXT: "Give us Feedback",
        BRANDING_ORGANIZATION_NAME: "OneKingdom Team",
        BRANDING_ORGANIZATION_URL: "https://onekingdom.team/",
    }

    for key, value in defaults.items():
        try:
            data.get_one(key)
        except RecordNotFound:
            setting = InstanceSetting(setting_key=key, setting_value=value)
            data.create(setting)
            print(f"Created default setting: {key}")


def get_branding_settings() -> BrandingSettings:
    """Get all branding settings as a BrandingSettings model."""
    branding_data = {}

    # Map database keys to model field names
    key_mapping = {
        BRANDING_LOGO: "logo_filename",
        BRANDING_FAVICON: "favicon_filename",
        BRANDING_FEEDBACK_URL: "feedback_url",
        BRANDING_FEEDBACK_TEXT: "feedback_button_text",
        BRANDING_ORGANIZATION_NAME: "organization_name",
        BRANDING_ORGANIZATION_URL: "organization_url",
    }

    settings = data.get_by_prefix("branding.")
    for setting in settings:
        if setting.setting_key in key_mapping:
            field_name = key_mapping[setting.setting_key]
            branding_data[field_name] = setting.setting_value

    return BrandingSettings(**branding_data)


def update_branding_settings(branding: BrandingSettings) -> BrandingSettings:
    """Update branding settings in the database."""
    settings_map = {
        BRANDING_LOGO: branding.logo_filename,
        BRANDING_FAVICON: branding.favicon_filename,
        BRANDING_FEEDBACK_URL: branding.feedback_url,
        BRANDING_FEEDBACK_TEXT: branding.feedback_button_text,
        BRANDING_ORGANIZATION_NAME: branding.organization_name,
        BRANDING_ORGANIZATION_URL: branding.organization_url,
    }

    for key, value in settings_map.items():
        if value is not None:
            setting = InstanceSetting(setting_key=key, setting_value=value)
            data.upsert(setting)

    return branding


def get_setting(key: str, default: str | None = None) -> str | None:
    """Get a single setting value by key, with optional default."""
    try:
        setting = data.get_one(key)
        return setting.setting_value
    except RecordNotFound:
        return default


def set_setting(key: str, value: str) -> InstanceSetting:
    """Set a setting value (create or update)."""
    setting = InstanceSetting(setting_key=key, setting_value=value)
    return data.upsert(setting)
