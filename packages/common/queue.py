from __future__ import annotations

import json

import redis.asyncio as redis

from packages.common.config import settings


QUEUE_KEY = "broadcast_queue"


async def _enqueue(payload: dict) -> None:
    client = redis.from_url(settings.redis_url)
    try:
        await client.rpush(QUEUE_KEY, json.dumps(payload))
    finally:
        await client.close()


async def enqueue_broadcast(payload: dict) -> None:
    payload = {"type": "broadcast", **payload}
    await _enqueue(payload)


async def enqueue_dm(
    user_id: int, message_text: str, parse_mode: str | None = None
) -> None:
    payload = {
        "type": "dm",
        "user_id": user_id,
        "message_text": message_text,
        "parse_mode": parse_mode,
    }
    await _enqueue(payload)
