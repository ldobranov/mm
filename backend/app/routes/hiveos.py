# FastAPI router for HiveOS proxy endpoints
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import logging
import requests
from typing import Optional

router = APIRouter(prefix="/api/v1/hiveos", tags=["HiveOS"])

class HiveOSFarmRequest(BaseModel):
    token: str
    farm_id: str

class HiveOSRigRequest(HiveOSFarmRequest):
    worker_id: str

class HiveOSActionRequest(HiveOSRigRequest):
    action: str

HIVEOS_API_BASE = "https://api2.hiveos.farm/api/v2"
ALLOWED_ACTIONS = [
    'miners/start',
    'miners/stop',
    'shutdown',
]

@router.post("/farm")
def get_farm(data: HiveOSFarmRequest):
    token = data.token
    farm_id = data.farm_id
    url = f"https://api2.hiveos.farm/api/v2/farms/{farm_id}/workers"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="HiveOS API request timed out")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"HiveOS API error: {str(e)}")
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return {"rigs": resp.json()["data"]}

@router.post("/rig")
def get_rig(data: HiveOSRigRequest):
    token = data.token
    farm_id = data.farm_id
    worker_id = data.worker_id
    url = f"https://api2.hiveos.farm/api/v2/farms/{farm_id}/workers/{worker_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
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
