from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.schedule import Schedule as ScheduleModel
from app.db.models.widget import Widget as WidgetModel

router = APIRouter(prefix="/api/v1/schedules", tags=["schedules"])

class ScheduleBase(BaseModel):
    widget_id: int
    action: str  # e.g. 'miners/start', 'miners/stop', 'shutdown'
    time: str    # ISO time string, e.g. '2025-06-26T21:00:00'
    repeat: Optional[str] = None  # e.g. 'daily', 'once', 'weekly'

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: int

@router.get("/", response_model=List[Schedule])
def list_schedules(db: Session = Depends(get_db)):
    return db.query(ScheduleModel).all()

@router.post("/", response_model=Schedule)
def create_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    # Validate widget exists
    widget = db.query(WidgetModel).filter(WidgetModel.id == schedule.widget_id).first()
    if not widget:
        raise HTTPException(status_code=400, detail="Widget not found")
    sched = ScheduleModel(**schedule.dict())
    db.add(sched)
    db.commit()
    db.refresh(sched)
    return sched

@router.put("/{schedule_id}", response_model=Schedule)
def update_schedule(schedule_id: int, schedule: ScheduleUpdate, db: Session = Depends(get_db)):
    sched = db.query(ScheduleModel).filter(ScheduleModel.id == schedule_id).first()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")
    for key, value in schedule.dict(exclude_unset=True).items():
        setattr(sched, key, value)
    db.commit()
    db.refresh(sched)
    return sched

@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    sched = db.query(ScheduleModel).filter(ScheduleModel.id == schedule_id).first()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")
    db.delete(sched)
    db.commit()
    return {"ok": True}
