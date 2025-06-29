from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base
import json

class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    languages = Column(String, nullable=False, default="en")
    site_name = Column(Text, nullable=False, default='{"en": "Global Virtual Display"}')
    site_content = Column(Text, nullable=True, default='{}')
    menu = Column(Text, nullable=True, default='[]')

    def get_site_name(self):
        try:
            return json.loads(self.site_name)
        except Exception:
            return {"en": self.site_name} if self.site_name else {"en": "Global Virtual Display"}

    def set_site_name(self, value):
        self.site_name = json.dumps(value)

    def get_site_content(self):
        try:
            return json.loads(self.site_content) if self.site_content else {}
        except Exception:
            return {"en": self.site_content} if self.site_content else {}

    def set_site_content(self, value):
        self.site_content = json.dumps(value)

    def get_menu(self):
        try:
            return json.loads(self.menu) if self.menu else []
        except Exception:
            return []

    def set_menu(self, value):
        self.menu = json.dumps(value)
