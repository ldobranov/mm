from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import asyncio

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

schedules_db: List[dict] = []

@router.get("/", response_model=List[Schedule])
def list_schedules():
    return schedules_db

@router.post("/", response_model=Schedule)
def create_schedule(schedule: ScheduleCreate):
    new_id = max([s["id"] for s in schedules_db], default=0) + 1
    sched = schedule.dict()
    sched["id"] = new_id
    schedules_db.append(sched)
    return sched

@router.put("/{schedule_id}", response_model=Schedule)
def update_schedule(schedule_id: int, schedule: ScheduleUpdate):
    for i, s in enumerate(schedules_db):
        if s["id"] == schedule_id:
            schedules_db[i].update(schedule.dict())
            return schedules_db[i]
    raise HTTPException(status_code=404, detail="Schedule not found")

@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int):
    for i, s in enumerate(schedules_db):
        if s["id"] == schedule_id:
            schedules_db.pop(i)
            return {"ok": True}
    raise HTTPException(status_code=404, detail="Schedule not found")

# Background task to check and trigger schedules
async def schedule_worker():
    while True:
        now = datetime.now().isoformat(timespec='seconds')
        for sched in schedules_db:
            # Only trigger if time matches now (to the minute)
            if sched["time"][:16] == now[:16]:
                # Here you would trigger the widget action (call the widget API)
                # For now, just print
                print(f"Triggering action {sched['action']} for widget {sched['widget_id']} at {now}")
                # TODO: Call the widget action API here
        await asyncio.sleep(30)

# To start the worker, add this to your FastAPI startup event:
# import asyncio
# @app.on_event("startup")
# async def start_schedule_worker():
#     asyncio.create_task(schedule_worker())
