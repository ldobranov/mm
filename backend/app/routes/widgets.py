from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.widget import Widget as WidgetModel
import os
import zipfile
import shutil

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

WIDGETS_BASE_DIR = os.path.join(os.path.dirname(__file__), '../../widgets')

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

# Move /available endpoint above /{widget_id} to avoid path conflict
@router.get("/available")
def list_available_widgets():
    if not os.path.exists(WIDGETS_BASE_DIR):
        return {"widgets": []}
    widgets = [d for d in os.listdir(WIDGETS_BASE_DIR) if os.path.isdir(os.path.join(WIDGETS_BASE_DIR, d))]
    return {"widgets": widgets}

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

@router.post("/upload")
def upload_widget(file: UploadFile = File(...)):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")
    widget_name = file.filename[:-4]
    widget_dir = os.path.join(WIDGETS_BASE_DIR, widget_name)
    if os.path.exists(widget_dir):
        shutil.rmtree(widget_dir)
    os.makedirs(widget_dir, exist_ok=True)
    zip_path = os.path.join(widget_dir, file.filename)
    with open(zip_path, "wb") as f:
        f.write(file.file.read())
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(widget_dir)
    except Exception as e:
        shutil.rmtree(widget_dir)
        raise HTTPException(status_code=400, detail=f"Invalid zip file: {e}")
    os.remove(zip_path)
    return {"status": "ok", "widget": widget_name}

@router.delete("/available/{widget_name}")
def delete_available_widget(widget_name: str):
    widget_dir = os.path.join(WIDGETS_BASE_DIR, widget_name)
    if not os.path.exists(widget_dir):
        raise HTTPException(status_code=404, detail="Widget not found")
    try:
        shutil.rmtree(widget_dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete widget: {e}")
    return {"ok": True}

@router.post("/install_full_zip")
def install_full_widget_zip(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Accepts a zip containing both frontend and backend widget code.
    Extracts frontend files to the widgets dir, backend files to backend/app/widgets/<name>.
    Also auto-registers the widget in the database if not present.
    Dynamically loads backend routes immediately after upload.
    """
    import tempfile, importlib
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")
    # Use a temp dir for extraction
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, file.filename)
        with open(zip_path, "wb") as f:
            f.write(file.file.read())
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid zip file: {e}")
        # Detect widget name/type from meta.json
        meta_path = os.path.join(tmpdir, 'meta.json')
        if not os.path.exists(meta_path):
            raise HTTPException(status_code=400, detail="meta.json missing in zip root")
        import json
        with open(meta_path) as f:
            meta = json.load(f)
        widget_type = meta.get('type') or meta.get('name') or 'unknown'
        # Copy frontend files
        widget_dir = os.path.join(WIDGETS_BASE_DIR, widget_type)
        if os.path.exists(widget_dir):
            shutil.rmtree(widget_dir)
        os.makedirs(widget_dir, exist_ok=True)
        for fname in ['HiveWidget.vue', 'meta.json', 'README.md']:
            src = os.path.join(tmpdir, fname)
            if os.path.exists(src):
                shutil.copy(src, widget_dir)
        # Copy backend files if present
        backend_dir = os.path.join(tmpdir, 'backend')
        if os.path.exists(backend_dir):
            dest_backend_dir = os.path.join(os.path.dirname(__file__), f'../widgets/{widget_type}')
            if os.path.exists(dest_backend_dir):
                shutil.rmtree(dest_backend_dir)
            # Ignore __pycache__ and only copy valid Python files/folders
            def ignore_func(dir, files):
                return [f for f in files if f == '__pycache__']
            shutil.copytree(backend_dir, dest_backend_dir, ignore=ignore_func)
            # Dynamically import and register backend routes, skip __pycache__
            try:
                import importlib.util
                import sys
                routes_path = os.path.join(dest_backend_dir, 'routes.py')
                if os.path.exists(routes_path):
                    module_name = f"app.widgets.{widget_type}.routes"
                    # Remove any __pycache__ or bad modules from sys.modules
                    for modname in list(sys.modules.keys()):
                        if modname.startswith("app.widgets.__pycache__") or modname.endswith(".__pycache__"):
                            del sys.modules[modname]
                    if module_name in sys.modules:
                        importlib.reload(sys.modules[module_name])
                    else:
                        mod = importlib.import_module(module_name)
                    from app.main import app as main_app
                    if hasattr(sys.modules[module_name], "router"):
                        main_app.include_router(sys.modules[module_name].router, prefix=f"/widgets/{widget_type}")
            except Exception as e:
                print(f"[Widget Install] Failed to load backend routes for {widget_type}: {e}")
        # Auto-register in DB if not present
        existing = db.query(WidgetModel).filter(WidgetModel.type == widget_type).first()
        if not existing:
            new_widget = WidgetModel(type=widget_type, enabled=True, config={}, size={}, pos={}, background=None)
            db.add(new_widget)
            db.commit()
            db.refresh(new_widget)
    return {"status": "ok", "widget": widget_type}

@router.post("/install_full_zip_modern")
def install_full_widget_zip_modern(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Accepts a modern widget zip with info.json, frontend/, backend/.
    Extracts frontend files to the widgets dir, backend files to backend/app/widgets/<name>.
    Registers the widget in the database and loads backend routes.
    Adds debug output for troubleshooting.
    """
    import tempfile, importlib, json, sys
    print("[DEBUG] install_full_zip_modern called")
    if not file.filename.endswith('.zip'):
        print("[DEBUG] File is not a zip: ", file.filename)
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, file.filename)
        print(f"[DEBUG] Saving uploaded zip to {zip_path}")
        with open(zip_path, "wb") as f:
            f.write(file.file.read())
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                print(f"[DEBUG] Extracting zip to {tmpdir}")
                zip_ref.extractall(tmpdir)
        except Exception as e:
            print(f"[DEBUG] Invalid zip file: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid zip file: {e}")
        info_path = os.path.join(tmpdir, 'info.json')
        print(f"[DEBUG] Looking for info.json at {info_path}")
        if not os.path.exists(info_path):
            print(f"[DEBUG] info.json missing in zip root, files in tmpdir: {os.listdir(tmpdir)}")
            raise HTTPException(status_code=400, detail="info.json missing in zip root")
        with open(info_path) as f:
            info = json.load(f)
        print(f"[DEBUG] Loaded info.json: {info}")
        widget_type = info.get('name') or info.get('type') or 'unknown'
        # Copy frontend files
        frontend_dir = os.path.join(tmpdir, 'frontend')
        widget_dir = os.path.join(WIDGETS_BASE_DIR, widget_type)
        print(f"[DEBUG] widget_type: {widget_type}, frontend_dir: {frontend_dir}, widget_dir: {widget_dir}")
        if os.path.exists(widget_dir):
            print(f"[DEBUG] Removing existing widget_dir: {widget_dir}")
            shutil.rmtree(widget_dir)
        if os.path.exists(frontend_dir):
            print(f"[DEBUG] Copying frontend_dir to widget_dir")
            shutil.copytree(frontend_dir, widget_dir)
        else:
            print(f"[DEBUG] frontend_dir does not exist: {frontend_dir}")
        # Copy backend files
        backend_dir = os.path.join(tmpdir, 'backend')
        dest_backend_dir = os.path.join(os.path.dirname(__file__), f'../widgets/{widget_type}')
        if os.path.exists(dest_backend_dir):
            print(f"[DEBUG] Removing existing dest_backend_dir: {dest_backend_dir}")
            shutil.rmtree(dest_backend_dir)
        if os.path.exists(backend_dir):
            print(f"[DEBUG] Copying backend_dir to dest_backend_dir")
            shutil.copytree(backend_dir, dest_backend_dir, ignore=shutil.ignore_patterns('__pycache__'))
            # Dynamically import and register backend routes
            try:
                routes_path = os.path.join(dest_backend_dir, 'routes.py')
                print(f"[DEBUG] Looking for backend routes at {routes_path}")
                if os.path.exists(routes_path):
                    module_name = f"app.widgets.{widget_type}.routes"
                    for modname in list(sys.modules.keys()):
                        if modname.startswith("app.widgets.__pycache__") or modname.endswith(".__pycache__"):
                            del sys.modules[modname]
                    if module_name in sys.modules:
                        print(f"[DEBUG] Reloading module {module_name}")
                        importlib.reload(sys.modules[module_name])
                    else:
                        print(f"[DEBUG] Importing module {module_name}")
                        mod = importlib.import_module(module_name)
                    from app.main import app as main_app
                    if hasattr(sys.modules[module_name], "router"):
                        print(f"[DEBUG] Including router for {module_name}")
                        main_app.include_router(sys.modules[module_name].router, prefix=f"/widgets/{widget_type}")
            except Exception as e:
                print(f"[Widget Install] Failed to load backend routes for {widget_type}: {e}")
        else:
            print(f"[DEBUG] backend_dir does not exist: {backend_dir}")
        # Auto-register in DB if not present
        existing = db.query(WidgetModel).filter(WidgetModel.type == widget_type).first()
        if not existing:
            print(f"[DEBUG] Registering widget in DB: {widget_type}")
            new_widget = WidgetModel(type=widget_type, enabled=True, config={}, size={}, pos={}, background=None)
            db.add(new_widget)
            db.commit()
            db.refresh(new_widget)
        else:
            print(f"[DEBUG] Widget already exists in DB: {widget_type}")
    print(f"[DEBUG] Widget install complete: {widget_type}")
    return {"status": "ok", "widget": widget_type, "info": info}
