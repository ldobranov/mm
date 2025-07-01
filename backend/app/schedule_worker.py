import asyncio
from sqlalchemy.orm import sessionmaker
from app.db.session import engine
from app.db.models.schedule import Schedule
from datetime import datetime, timezone

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def schedule_worker():
    while True:
        now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        with SessionLocal() as db:
            schedules = db.query(Schedule).all()
            for sched in schedules:
                try:
                    sched_time = datetime.fromisoformat(sched.time)
                except Exception:
                    continue
                if sched_time.replace(second=0, microsecond=0) == now:
                    try:
                        sched.trigger(db)
                    except Exception:
                        pass
        await asyncio.sleep(30)
