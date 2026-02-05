from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from packages.db.repo_leaderboard import get_leaderboard, get_user_rank
from packages.db.repo_submissions import upsert_user
from packages.db.session import async_session_maker

router = Router()


def _display_name(username: str | None, tg_id: int) -> str:
    if username:
        return f"@{username}"
    return f"User {str(tg_id)[-4:]}"


@router.message(Command("top"))
async def cmd_top(message: Message) -> None:
    async with async_session_maker() as session:
        await upsert_user(
            session,
            message.from_user.id,
            message.from_user.username if message.from_user else None,
        )
        board = await get_leaderboard(session, limit=10)
        me = await get_user_rank(session, message.from_user.id)

    if not board:
        await message.answer("Henüz leaderboard boş. İlk puanı kapan sen ol.")
        return

    lines = ["Leaderboard (Top 10)\n"]
    for i, row in enumerate(board, start=1):
        name = _display_name(row["username"], row["telegram_user_id"])
        points = row["points"]
        marker = "  " if row["telegram_user_id"] == message.from_user.id else ""
        lines.append(f"{i}. {name} — {points}⭐{marker}")

    if me["rank"] is None:
        lines.append("\nSen: 0⭐ (henüz sıralamada yoksun)")
    else:
        lines.append(f"\nSenin sıralaman: #{me['rank']} — {me['points']}⭐")

    await message.answer("\n".join(lines))
