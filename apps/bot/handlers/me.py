from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from packages.common.config import settings
from packages.db.repo_profile import get_profile_stats, get_referral_stats
from packages.db.repo_submissions import upsert_user
from packages.db.session import async_session_maker

router = Router()


@router.message(Command("me"))
async def cmd_me(message: Message) -> None:
    async with async_session_maker() as session:
        await upsert_user(
            session,
            message.from_user.id,
            message.from_user.username if message.from_user else None,
        )
        stats = await get_profile_stats(session, message.from_user.id)
        ref = await get_referral_stats(session, message.from_user.id)

    if not stats:
        await message.answer("Profil bulunamadı. /start")
        return

    user = stats["user"]
    bot_username = settings.bot_username.lstrip("@") or "Landofairdropbot"
    ref_link = f"https://t.me/{bot_username}?start=ref_{user.ref_code}"
    await message.answer(
        "Profil\n"
        f"User: @{user.username or '—'}\n"
        f"Wallet: {getattr(user, 'wallet_address', None) or '—'}\n\n"
        f"⭐ Toplam Puan: {stats['total_points']}\n"
        f"• Görev puanı: {stats['approved_points']}⭐\n"
        f"• Referral bonus: {stats['ref_bonus_points']}⭐\n\n"
        f"✅ Onaylanan görev: {stats['approved_count']}\n"
        f"⏳ Bekleyen: {stats['pending_count']}\n"
        f"Referral: {ref['ref_count']} kişi\n\n"
        f"Referral linkin:\n{ref_link}"
    )
