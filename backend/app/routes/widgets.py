from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

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

widgets_db = [
    {"id": 1, "type": "clock", "enabled": True, "config": {"style": "digital"}, "size": {"w": 200, "h": 100}, "pos": {"x": 20, "y": 40}},
    {"id": 2, "type": "date", "enabled": True, "config": {"format": "YYYY-MM-DD"}, "size": {"w": 200, "h": 100}, "pos": {"x": 240, "y": 40}},
    {"id": 3, "type": "temp", "enabled": False, "config": {}, "size": {"w": 200, "h": 100}, "pos": {"x": 460, "y": 40}},
]

router = APIRouter(prefix="/api/v1/widgets", tags=["widgets"])

@router.get("/", response_model=List[Widget])
def list_widgets():
    return widgets_db

@router.post("/", response_model=Widget)
def create_widget(widget: WidgetCreate):
    new_id = max(w["id"] for w in widgets_db) + 1 if widgets_db else 1
    new_widget = widget.dict()
    new_widget["id"] = new_id
    widgets_db.append(new_widget)
    return new_widget

@router.get("/{widget_id}", response_model=Widget)
def get_widget(widget_id: int):
    for w in widgets_db:
        if w["id"] == widget_id:
            return w
    raise HTTPException(status_code=404, detail="Widget not found")

@router.put("/{widget_id}", response_model=Widget)
def update_widget(widget_id: int, widget: WidgetUpdate):
    for i, w in enumerate(widgets_db):
        if w["id"] == widget_id:
            # Only update fields present in the request (partial update)
            update_data = widget.dict(exclude_unset=True)
            widgets_db[i].update(update_data)
            return widgets_db[i]
    raise HTTPException(status_code=404, detail="Widget not found")

@router.delete("/{widget_id}")
def delete_widget(widget_id: int):
    for i, w in enumerate(widgets_db):
        if w["id"] == widget_id:
            widgets_db.pop(i)
            return {"ok": True}
    raise HTTPException(status_code=404, detail="Widget not found")
