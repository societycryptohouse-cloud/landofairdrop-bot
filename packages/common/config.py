from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def _env_list(key: str) -> list[int]:
    raw = _env(key)
    if not raw:
        return []
    return [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]


def _env_int(key: str) -> int | None:
    raw = _env(key)
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


@dataclass(frozen=True)
class Settings:
    bot_token: str = _env("BOT_TOKEN")
    database_url: str = _env("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    redis_url: str = _env("REDIS_URL")
    admin_user_ids: list[int] = field(default_factory=lambda: _env_list("ADMIN_USER_IDS"))
    webhook_url: str = _env("WEBHOOK_URL")
    env: str = _env("ENV", "local")

    bot_name: str = _env("BOT_NAME", "Land of Airdrop")
    bot_username: str = _env("BOT_USERNAME", "@Landofairdropbot")

    tg_announce_channel: str = _env("TG_ANNOUNCE_CHANNEL", "@placeholder_channel")
    tg_community_group: str = _env("TG_COMMUNITY_GROUP", "@placeholder_group")
    tg_join_check_channel_id: str = _env("TG_JOIN_CHECK_CHANNEL_ID", "")
    tg_join_channel: str | None = _env("TG_JOIN_CHANNEL", "") or None
    tg_join_channel_id: int | None = _env_int("TG_JOIN_CHANNEL_ID")

    task_x_account: str = _env("TASK_X_ACCOUNT", "@placeholder_x")
    task_discord_invite: str = _env("TASK_DISCORD_INVITE", "https://discord.gg/placeholder")

    broadcast_per_second: int = _env_int("BROADCAST_PER_SECOND") or 10

    referral_bonus_points: int = _env_int("REFERRAL_BONUS_POINTS") or 10


settings = Settings()
