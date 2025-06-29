# FastAPI router for HiveOS proxy endpoints
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import logging

router = APIRouter(prefix="/api/v1/hiveos", tags=["HiveOS"])

class HiveOSRigRequest(BaseModel):
    token: str
    farm_id: str
    worker_id: str

class HiveOSActionRequest(HiveOSRigRequest):
    action: str

HIVEOS_API_BASE = "https://api2.hiveos.farm/api/v2"
ALLOWED_ACTIONS = [
    'miners/start',
    'miners/stop',
    'shutdown',
]

@router.post("/rig")
async def get_rig(data: HiveOSRigRequest):
    url = f"{HIVEOS_API_BASE}/farms/{data.farm_id}/workers/{data.worker_id}"
    headers = {"Authorization": f"Bearer {data.token}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

@router.post("/rig/action")
async def rig_action(data: HiveOSActionRequest):
    if data.action not in ALLOWED_ACTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid action: {data.action}")
    headers = {"Authorization": f"Bearer {data.token}"}
    if data.action in ("miners/start", "miners/stop"):
        # Use /command endpoint for miner actions
        url = f"{HIVEOS_API_BASE}/farms/{data.farm_id}/workers/{data.worker_id}/command"
        miner_action = "start" if data.action == "miners/start" else "stop"
        payload = {"command": "miner", "data": {"action": miner_action}}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code not in (200, 202):
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            return {"status": "ok"}
    elif data.action == "shutdown":
        url = f"{HIVEOS_API_BASE}/farms/{data.farm_id}/workers/{data.worker_id}/shutdown"
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers)
            if resp.status_code not in (200, 202):
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            return {"status": "ok"}
