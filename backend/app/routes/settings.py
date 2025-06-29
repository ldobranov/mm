from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.settings import Settings
from app.schemas.settings import SettingsSchema
from app.routes.deps import get_current_admin_user

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])

@router.get("", response_model=SettingsSchema)
def get_settings(db: Session = Depends(get_db)):
    """Get site settings."""
    settings = db.query(Settings).first()
    if not settings:
        return SettingsSchema()
    return SettingsSchema(
        languages=settings.languages.split(","),
        siteName=settings.get_site_name(),
        siteContent=settings.get_site_content(),
        menu=settings.get_menu(),
    )

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

    def menu_to_dict(menu):
        if isinstance(menu, list):
            return [menu_to_dict(m) for m in menu]
        if hasattr(menu, 'dict'):
            d = menu.dict()
            if 'children' in d:
                d['children'] = menu_to_dict(d['children'])
            return d
        return menu

    settings.set_menu(menu_to_dict(data.menu))
    db.commit()
    db.refresh(settings)
    return SettingsSchema(
        languages=settings.languages.split(","),
        siteName=settings.get_site_name(),
        siteContent=settings.get_site_content(),
        menu=settings.get_menu(),
    )