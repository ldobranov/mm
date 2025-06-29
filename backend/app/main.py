from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.settings import router as settings_router
from app.routes.user import router as user_router
from app.routes.category import router as category_router
from app.routes.api import router as api_router
from app.routes.widgets import router as widgets_router
from app.routes.hiveos import router as hiveos_router
from app.routes.schedules import router as schedules_router, schedule_worker
from app.create_tables import create_tables

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_tables()

app.include_router(user_router)
app.include_router(category_router)
app.include_router(settings_router)
app.include_router(api_router)
app.include_router(widgets_router)
app.include_router(hiveos_router)
app.include_router(schedules_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Fullstack App!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

import asyncio
@app.on_event("startup")
async def start_schedule_worker():
    asyncio.create_task(schedule_worker())