from fastapi import APIRouter, Body
import os
import json

router = APIRouter()

WIDGET_DIR = os.path.dirname(__file__)

@router.get("/template")
def get_template():
    path = os.path.join(WIDGET_DIR, "template.html")
    if not os.path.exists(path):
        return {"error": "Not found"}
    with open(path) as f:
        return {"content": f.read()}

@router.post("/template")
def update_template(body: dict = Body(...)):
    path = os.path.join(WIDGET_DIR, "template.html")
    with open(path, "w") as f:
        f.write(body["content"])
    return {"status": "ok"}

@router.get("/meta")
def get_meta():
    path = os.path.join(WIDGET_DIR, "meta.json")
    if not os.path.exists(path):
        return {"error": "Not found"}
    with open(path) as f:
        return json.load(f)

@router.post("/meta")
def update_meta(body: dict = Body(...)):
    path = os.path.join(WIDGET_DIR, "meta.json")
    with open(path, "w") as f:
        json.dump(body, f, indent=2)
    return {"status": "ok"}
