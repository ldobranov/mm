from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    selectable = Column(Boolean, default=True, nullable=False)
    order = Column(Integer, default=0, nullable=False)
    parent = relationship('Category', remote_side=[id], backref='children', uselist=False)
    items = relationship("Item", secondary="item_categories", back_populates="categories")