from sqlalchemy import Column, Integer, String, JSON
from app.database import Base

class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    languages = Column(JSON, default=["en"])
    site_name = Column(JSON, default={"en": ""})
    site_content = Column(JSON, default={"en": ""})
    menu = Column(JSON, default=[])
