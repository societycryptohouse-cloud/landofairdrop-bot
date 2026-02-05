from __future__ import annotations

import asyncio
import json

import redis.asyncio as redis
from aiogram import Bot

from packages.common.config import settings
from packages.common.queue import QUEUE_KEY


async def run_broadcast(bot: Bot, payload: dict, per_second: int) -> dict:
    delay = 1.0 / max(per_second, 1)
    ok, fail = 0, 0

    for uid in payload.get("user_ids", []):
        try:
            await bot.send_message(uid, payload.get("message_text", ""), parse_mode=payload.get("parse_mode"))
            ok += 1
        except Exception:
            fail += 1
        await asyncio.sleep(delay)

    return {"ok": ok, "fail": fail}


async def worker_loop() -> None:
    client = redis.from_url(settings.redis_url)
    bot = Bot(token=settings.bot_token)
    per_second = settings.broadcast_per_second

    try:
        while True:
            item = await client.blpop(QUEUE_KEY, timeout=5)
            if not item:
                continue
            _key, raw = item
            payload = json.loads(raw)
            payload_type = payload.get("type")
            if payload_type == "dm":
                uid = payload.get("user_id")
                text = payload.get("message_text", "")
                if uid and text:
                    try:
                        await bot.send_message(uid, text, parse_mode=payload.get("parse_mode"))
                    except Exception:
                        pass
                continue

            if payload_type == "broadcast":
                result = await run_broadcast(bot, payload, per_second)
                print(f"Broadcast done: ok={result['ok']} fail={result['fail']}")
                continue
    finally:
        await bot.session.close()
        await client.close()


def main() -> None:
    asyncio.run(worker_loop())


if __name__ == "__main__":
    main()
