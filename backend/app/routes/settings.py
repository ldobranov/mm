from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.settings import Settings
from app.schemas.settings import SettingsSchema
from app.routes.deps import get_current_admin_user
import json

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])

@router.get("", response_model=SettingsSchema)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        # Only create defaults if settings row does not exist
        return {
            "languages": ["en"],
            "siteName": {"en": ""},
            "siteContent": {"en": ""},
            "menu": []
        }

    def parse_json_field(val, default):
        if val is None or val == "":
            return default
        if isinstance(val, dict) or isinstance(val, list):
            return val
        try:
            return json.loads(val)
        except Exception:
            return default

    # Handle languages (could be comma-separated or JSON)
    langs = settings.languages
    if isinstance(langs, list):
        languages = langs
    elif isinstance(langs, str):
        if langs.strip().startswith("["):
            try:
                languages = json.loads(langs)
            except Exception:
                languages = [l.strip() for l in langs.split(",") if l.strip()]
        else:
            languages = [l.strip() for l in langs.split(",") if l.strip()]
    else:
        languages = ["en"]

    return {
        "languages": languages,
        "siteName": parse_json_field(settings.site_name, {"en": ""}),
        "siteContent": parse_json_field(settings.site_content, {"en": ""}),
        "menu": parse_json_field(settings.menu, []),
    }

@router.put("", response_model=SettingsSchema)
def update_settings(
    data: SettingsSchema,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin_user)
):
    """Update site settings."""
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings()
        db.add(settings)
    settings.languages = ",".join(data.languages)
    settings.set_site_name(data.siteName)
    settings.set_site_content(data.siteContent)
    # Serialize menu to JSON string before saving
    import json
    settings.menu = json.dumps([m.dict() if hasattr(m, "dict") else m for m in data.menu])
    db.commit()
    db.refresh(settings)
    return {
        "languages": settings.languages.split(","),
        "siteName": settings.get_site_name(),
        "siteContent": settings.get_site_content(),
        "menu": settings.get_menu(),
    }