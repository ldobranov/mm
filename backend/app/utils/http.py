import httpx
import logging

async def safe_get(url, headers=None, params=None, retries=2):
    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(url, headers=headers, params=params, timeout=10)
                r.raise_for_status()
                return r.json()
        except httpx.HTTPError as e:
            logging.warning(f"[HTTP ERROR] GET {url} failed (attempt {attempt+1}): {e}")
    return None

async def safe_post(url, headers=None, data=None, json=None, retries=2):
    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(url, headers=headers, data=data, json=json, timeout=10)
                r.raise_for_status()
                return r.json()
        except httpx.HTTPError as e:
            logging.warning(f"[HTTP ERROR] POST {url} failed (attempt {attempt+1}): {e}")
    return None
