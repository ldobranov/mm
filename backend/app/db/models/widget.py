from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class Widget(Base):
    __tablename__ = "widgets"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    config = Column(JSON, default={})
    size = Column(JSON, default={})
    pos = Column(JSON, default={})
    background = Column(String, nullable=True)
    name = Column(String, nullable=True)
    schedules = relationship("Schedule", back_populates="widget", cascade="all, delete-orphan")

    def run_action(self, action: str, config: dict = None, db=None):
        updated = False
        if action == "enable":
            self.enabled = True
            updated = True
        elif action == "disable":
            self.enabled = False
            updated = True
        # Add more actions as needed
        if updated and db is not None:
            db.add(self)
            db.commit()
            db.refresh(self)
