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
    # Get all workers in the farm
    workers_url = f"{HIVEOS_API_BASE}/farms/{farm_id}/workers"
    workers_result = await safe_get(workers_url, headers=headers)
    if not workers_result or "data" not in workers_result:
        logger.warning(f"HiveOS API error: {workers_result}")
        raise HTTPException(status_code=502, detail="HiveOS API error (fetching workers)")
    results = []
    for worker in workers_result["data"]:
        worker_id = worker.get("id") or worker.get("worker_id")
        if not worker_id:
            logger.warning(f"Worker missing id: {worker}")
            results.append({"worker_id": None, "status": "error", "error": "missing_id"})
            continue
        url = f"{HIVEOS_API_BASE}/farms/{farm_id}/workers/{worker_id}/command"
        if data.action in ["miners/start", "miners/stop"]:
            miner_action = "start" if data.action == "miners/start" else "stop"
            payload = {"command": "miner", "data": {"action": miner_action}}
        elif data.action in ["reboot", "shutdown"]:
            payload = {"command": data.action}
        else:
            logger.warning(f"Unsupported action: {data.action}")
            results.append({"worker_id": worker_id, "status": "error", "error": "unsupported_action"})
            continue
        try:
            result = await safe_post(url, headers=headers, json=payload)
            if result:
                results.append({"worker_id": worker_id, "status": "ok"})
            else:
                logger.warning(f"HiveOS {data.action} failed for worker {worker_id}")
                results.append({"worker_id": worker_id, "status": "error", "error": "no_result"})
        except Exception as e:
            logger.warning(f"HiveOS {data.action} failed for worker {worker_id}: {e}")
            results.append({"worker_id": worker_id, "status": "error", "error": str(e)})
    return {"results": results}

@router.post("/rig/action")
@retry(times=2)
async def rig_action(data: HiveOSActionRequest):
    if data.action not in ALLOWED_ACTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid action: {data.action}")
    if not data.worker_id:
        logger.warning(f"Missing worker_id in rig_action: {data}")
        raise HTTPException(status_code=422, detail="worker_id is required for rig actions")
    headers = {"Authorization": f"Bearer {data.token or get_config('HIVE_TOKEN')}", "Content-Type": "application/json"}
    farm_id = data.farm_id or get_config('HIVE_FARM_ID')
    worker_id = data.worker_id
    if data.action in ["miners/start", "miners/stop"]:
        url = f"{HIVEOS_API_BASE}/farms/{farm_id}/workers/{worker_id}/command"
        miner_action = "start" if data.action == "miners/start" else "stop"
        payload = {"command": "miner", "data": {"action": miner_action}}
        try:
            result = await safe_post(url, headers=headers, json=payload)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"HiveOS {data.action} not supported for worker {worker_id}")
                raise HTTPException(status_code=404, detail=f"{data.action.capitalize()} not supported for this rig (worker_id={worker_id})")
            raise
        if not result:
            logger.warning(f"HiveOS {data.action} failed for worker {worker_id}")
            raise HTTPException(status_code=502, detail=f"HiveOS {data.action} failed for worker {worker_id}")
        return {"status": "ok"}
    elif data.action in ["reboot", "shutdown"]:
        url = f"{HIVEOS_API_BASE}/farms/{farm_id}/workers/{worker_id}/command"
        payload = {"command": data.action}
        try:
            result = await safe_post(url, headers=headers, json=payload)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"HiveOS {data.action} not supported for worker {worker_id}")
                raise HTTPException(status_code=404, detail=f"{data.action.capitalize()} not supported for this rig (worker_id={worker_id})")
            raise
        if not result:
            logger.warning(f"HiveOS {data.action} failed for worker {worker_id}")
            raise HTTPException(status_code=502, detail=f"HiveOS {data.action} failed for worker {worker_id}")
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=400, detail="Unsupported rig action")
