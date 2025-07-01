# FastAPI router for HiveOS proxy endpoints
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import requests
from typing import Optional
from app.utils.http import safe_get, safe_post
from app.utils.config import get_config
from app.utils.logger import get_logger
from app.utils.decorators import retry

router = APIRouter(prefix="/api/v1/hiveos", tags=["HiveOS"])
logger = get_logger("hiveos")

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
    'reboot',
]

@router.post("/farm")
@retry(times=2)
async def get_farm(data: HiveOSFarmRequest):
    token = data.token or get_config("HIVE_TOKEN")
    farm_id = data.farm_id or get_config("HIVE_FARM_ID")
    url = f"https://api2.hiveos.farm/api/v2/farms/{farm_id}/workers"
    headers = {"Authorization": f"Bearer {token}"}
    result = await safe_get(url, headers=headers)
    if not result or "data" not in result:
        logger.warning(f"HiveOS API error: {result}")
        raise HTTPException(status_code=502, detail="HiveOS API error")
    return {"rigs": result["data"]}

@router.post("/rig")
@retry(times=2)
async def get_rig(data: HiveOSRigRequest):
    token = data.token or get_config("HIVE_TOKEN")
    farm_id = data.farm_id or get_config("HIVE_FARM_ID")
    worker_id = data.worker_id
    url = f"https://api2.hiveos.farm/api/v2/farms/{farm_id}/workers/{worker_id}"
    headers = {"Authorization": f"Bearer {token}"}
    result = await safe_get(url, headers=headers)
    if not result:
        logger.warning(f"HiveOS API error: {result}")
        raise HTTPException(status_code=502, detail="HiveOS API error")
    return result

@router.post("/farm/action")
@retry(times=2)
async def farm_action(data: HiveOSActionRequest):
    if data.action not in ALLOWED_ACTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid action: {data.action}")
    headers = {"Authorization": f"Bearer {data.token or get_config('HIVE_TOKEN')}", "Content-Type": "application/json"}
    farm_id = data.farm_id or get_config('HIVE_FARM_ID')
    # Farm-wide miner start/stop
    if data.action in ("miners/start", "miners/stop"):
        url = f"{HIVEOS_API_BASE}/farms/{farm_id}/workers/command"
        miner_action = "start" if data.action == "miners/start" else "stop"
        payload = {"command": "miner", "data": {"action": miner_action}}
        result = await safe_post(url, headers=headers, json=payload)
        if not result:
            logger.warning(f"HiveOS farm miner action failed: {data.action}")
            raise HTTPException(status_code=502, detail="HiveOS farm miner action failed")
        return {"status": "ok"}
    elif data.action == "shutdown":
        url = f"{HIVEOS_API_BASE}/farms/{farm_id}/shutdown"
        result = await safe_post(url, headers=headers)
        if not result:
            logger.warning(f"HiveOS farm shutdown failed for farm {farm_id}")
            raise HTTPException(status_code=502, detail="HiveOS farm shutdown failed")
        return {"status": "ok"}
    elif data.action == "reboot":
        url = f"{HIVEOS_API_BASE}/farms/{farm_id}/reboot"
        result = await safe_post(url, headers=headers)
        if not result:
            logger.warning(f"HiveOS farm reboot failed for farm {farm_id}")
            raise HTTPException(status_code=502, detail="HiveOS farm reboot failed")
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=400, detail="Unsupported farm action")

@router.post("/rig/action")
@retry(times=2)
async def rig_action(data: HiveOSActionRequest):
    if data.action not in ALLOWED_ACTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid action: {data.action}")
    headers = {"Authorization": f"Bearer {data.token or get_config('HIVE_TOKEN')}", "Content-Type": "application/json"}
    farm_id = data.farm_id or get_config('HIVE_FARM_ID')
    worker_id = data.worker_id
    if data.action in ("miners/start", "miners/stop"):
        url = f"{HIVEOS_API_BASE}/farms/{farm_id}/workers/{worker_id}/command"
        miner_action = "start" if data.action == "miners/start" else "stop"
        payload = {"command": "miner", "data": {"action": miner_action}}
        result = await safe_post(url, headers=headers, json=payload)
        if not result:
            logger.warning(f"HiveOS miner action failed: {data.action}")
            raise HTTPException(status_code=502, detail="HiveOS miner action failed")
        return {"status": "ok"}
    elif data.action == "shutdown":
        url = f"{HIVEOS_API_BASE}/farms/{farm_id}/workers/{worker_id}/shutdown"
        result = await safe_post(url, headers=headers)
        if not result:
            logger.warning(f"HiveOS shutdown failed for worker {worker_id}")
            raise HTTPException(status_code=502, detail="HiveOS shutdown failed")
        return {"status": "ok"}
    elif data.action == "reboot":
        url = f"{HIVEOS_API_BASE}/farms/{farm_id}/workers/{worker_id}/reboot"
        result = await safe_post(url, headers=headers)
        if not result:
            logger.warning(f"HiveOS reboot failed for worker {worker_id}")
            raise HTTPException(status_code=502, detail="HiveOS reboot failed")
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=400, detail="Unsupported rig action")
