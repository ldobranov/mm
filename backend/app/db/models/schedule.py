from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    widget_id = Column(Integer, ForeignKey("widgets.id"), nullable=False)
    action = Column(String, nullable=False)
    time = Column(String, nullable=False)  # ISO string
    repeat = Column(String, nullable=True)

    widget = relationship("Widget", back_populates="schedules")

    def trigger(self, db):
        from app.db.models.widget import Widget
        widget = db.query(Widget).get(self.widget_id)
        if widget:
            widget.run_action(self.action, db=db)
