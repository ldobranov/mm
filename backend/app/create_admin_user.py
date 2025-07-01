import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.users import User
from app.db.models.widget import Widget
from app.db.models.schedule import Schedule
from app.db.models.settings import Settings
from passlib.context import CryptContext
import json

def seed_widgets(db):
    widgets = [
        Widget(type='clock', enabled=True, config={}, size={}, pos={}, background=None, name='Clock'),
        Widget(type='date', enabled=True, config={}, size={}, pos={}, background=None, name='Date'),
        Widget(type='temp', enabled=True, config={}, size={}, pos={}, background=None, name='Temp'),
        Widget(type='hive', enabled=True, config={}, size={}, pos={}, background=None, name='Hive'),
    ]
    for w in widgets:
        exists = db.query(Widget).filter(Widget.type == w.type).first()
        if not exists:
            db.add(w)
    db.commit()
    print("Default widgets seeded.")

def seed_menu_and_settings(db):
    menu = [
        {"id": 1, "label": {"en": "Display"}, "route": "/display", "visibility": "public", "children": []},
        {"id": 2, "label": {"en": "Widget"}, "route": "/widget", "visibility": "public", "children": []},
        {"id": 3, "label": {"en": "Schedules"}, "route": "/schedules", "visibility": "public", "children": []},
        {"id": 4, "label": {"en": "Settings"}, "route": "/settings", "visibility": "public", "children": []},
        {"id": 5, "label": {"en": "Users"}, "route": "/users", "visibility": "public", "children": []},
    ]
    settings = db.query(Settings).first()
    if not settings:
        settings = Settings(languages="en", site_name=json.dumps({"en": "Global Virtual Display"}), site_content=json.dumps({}), menu=json.dumps(menu))
        db.add(settings)
    else:
        settings.menu = json.dumps(menu)
    db.commit()
    print("Menu and settings seeded.")

def seed_schedules(db):
    widget = db.query(Widget).filter(Widget.type == 'hive').first()
    if widget:
        exists = db.query(Schedule).filter(Schedule.widget_id == widget.id, Schedule.action == 'miners/start').first()
        if not exists:
            sched = Schedule(widget_id=widget.id, action='miners/start', time='2025-07-01T12:00:00', repeat='once')
            db.add(sched)
            db.commit()
            print("Default schedule seeded.")

def create_admin_user():
    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@admin.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin")
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(admin_password)

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == admin_username).first()
        if not user:
            user = User(
                username=admin_username,
                email=admin_email,
                hashed_password=hashed_password,
                role="admin"
            )
            db.add(user)
            db.commit()
            print(f"Admin user '{admin_username}' created.")
        else:
            print(f"Admin user '{admin_username}' already exists.")
        seed_widgets(db)
        seed_menu_and_settings(db)
        seed_schedules(db)
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
