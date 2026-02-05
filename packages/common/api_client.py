from __future__ import annotations

import httpx

from packages.common.config import settings


def _headers() -> dict:
    return {"x-api-key": settings.api_key, "content-type": "application/json"}


async def api_get(path: str) -> dict:
    url = settings.api_base_url.rstrip("/") + path
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers=_headers())
        resp.raise_for_status()
        return resp.json()


async def api_post(path: str, payload: dict) -> dict:
    url = settings.api_base_url.rstrip("/") + path
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, headers=_headers(), json=payload)
        resp.raise_for_status()
        return resp.json()
