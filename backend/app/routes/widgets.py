from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.widget import Widget as WidgetModel

class WidgetBase(BaseModel):
    type: str  # 'clock', 'date', 'temp', 'hive'
    enabled: bool
    config: Optional[dict] = None
    size: Optional[dict] = None  # {w: int, h: int}
    pos: Optional[dict] = None   # {x: int, y: int}
    background: Optional[str] = None

class WidgetCreate(WidgetBase):
    pass

class WidgetUpdate(WidgetBase):
    pass

class Widget(WidgetBase):
    id: int

router = APIRouter(prefix="/api/v1/widgets", tags=["widgets"])

@router.get("/", response_model=List[Widget])
def list_widgets(db: Session = Depends(get_db)):
    return db.query(WidgetModel).all()

@router.post("/", response_model=Widget)
def create_widget(widget: WidgetCreate, db: Session = Depends(get_db)):
    new_widget = WidgetModel(**widget.dict())
    db.add(new_widget)
    db.commit()
    db.refresh(new_widget)
    return new_widget

@router.get("/{widget_id}", response_model=Widget)
def get_widget(widget_id: int, db: Session = Depends(get_db)):
    widget = db.query(WidgetModel).filter(WidgetModel.id == widget_id).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    return widget

@router.put("/{widget_id}", response_model=Widget)
def update_widget(widget_id: int, widget: WidgetUpdate, db: Session = Depends(get_db)):
    db_widget = db.query(WidgetModel).filter(WidgetModel.id == widget_id).first()
    if not db_widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    for key, value in widget.dict(exclude_unset=True).items():
        setattr(db_widget, key, value)
    db.commit()
    db.refresh(db_widget)
    return db_widget

@router.delete("/{widget_id}")
def delete_widget(widget_id: int, db: Session = Depends(get_db)):
    db_widget = db.query(WidgetModel).filter(WidgetModel.id == widget_id).first()
    if not db_widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    db.delete(db_widget)
    db.commit()
    return {"ok": True}
