from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.common.config import settings
from packages.db.models import Task


def _tg_meta() -> dict:
    channel = settings.tg_join_channel or "@_____"
    channel_id = settings.tg_join_channel_id
    if channel_id:
        return {"channel": channel, "channel_id": channel_id}
    return {"channel": channel, "channel_id": None}

DEFAULT_TASKS = [
    {
        "key": "tg_join_channel",
        "type": "telegram_auto",
        "title": "Telegram kanalına katıl",
        "description": "Duyuru kanalına katıl ve kontrol et.",
        "points": 50,
        "meta": _tg_meta(),
        "is_active": True,
    },
    {
        "key": "x_follow",
        "type": "proof_required",
        "title": "X hesabını takip et",
        "description": "Takip ettiğini kanıt olarak link veya ekran görüntüsü ile ilet.",
        "points": 30,
        "meta": {
            "x_account": "@_____",
            "proof_hint": "Profil ekran görüntüsü veya takip ettiğini gösteren link",
        },
        "is_active": True,
    },
    {
        "key": "discord_join",
        "type": "proof_required",
        "title": "Discord sunucusuna katıl",
        "description": "Sunucuya katıldığını kanıt olarak kullanıcı adını veya ekran görüntüsü ile ilet.",
        "points": 20,
        "meta": {
            "invite_link": "https://discord.gg/_____",
            "proof_hint": "Discord kullanıcı adını yaz veya ekran görüntüsü paylaş",
        },
        "is_active": True,
    },
]


async def seed_tasks(session: AsyncSession, tasks=DEFAULT_TASKS) -> dict:
    """
    Idempotent seed: var olan task'leri key üzerinden günceller, yoksa ekler.
    """
    created, updated = 0, 0

    for t in tasks:
        existing = await session.scalar(select(Task).where(Task.key == t["key"]))
        if existing:
            existing.type = t["type"]
            existing.title = t["title"]
            existing.description = t["description"]
            existing.points = t["points"]
            existing.meta = t["meta"]
            existing.is_active = t["is_active"]
            updated += 1
        else:
            session.add(Task(**t))
            created += 1

    await session.commit()
    return {"created": created, "updated": updated}
