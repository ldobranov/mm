from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.settings import router as settings_router
from app.routes.user import router as user_router
from app.routes.category import router as category_router
from app.routes.api import router as api_router
from app.routes.widgets import router as widgets_router
from app.routes.hiveos import router as hiveos_router
from app.routes.schedules import router as schedules_router
from app.create_tables import create_tables
import importlib
import os
import asyncio
from app.schedule_worker import schedule_worker

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_tables()

@app.on_event("startup")
async def start_schedule_worker():
    asyncio.create_task(schedule_worker())

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

def load_widgets(app):
    widgets_dir = os.path.join(os.path.dirname(__file__), "widgets")
    if not os.path.exists(widgets_dir):
        return
    for widget in os.listdir(widgets_dir):
        widget_path = os.path.join(widgets_dir, widget)
        if os.path.isdir(widget_path):
            try:
                mod = importlib.import_module(f"app.widgets.{widget}.routes")
                if hasattr(mod, "router"):
                    app.include_router(mod.router, prefix=f"/widgets/{widget}")
                    print(f"✅ Loaded widget: {widget}")
            except Exception as e:
                print(f"❌ Failed to load {widget}: {e}")

load_widgets(app)

if __name__ == "__main__":
    import uvicorn
    import os
    host = os.environ.get("BACKEND_HOST", "0.0.0.0")
    port = int(os.environ.get("BACKEND_PORT", "8887"))
    uvicorn.run(app, host=host, port=port)