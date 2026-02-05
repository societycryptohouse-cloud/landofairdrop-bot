from __future__ import annotations

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from packages.db.repo_submissions import (
    get_task_by_key,
    upsert_auto_approved_submission,
    upsert_user,
)
from packages.db.session import async_session_maker

router = Router()

MEMBER_OK = {"member", "administrator", "creator"}


@router.callback_query(F.data.startswith("check:"))
async def cb_check_task(cb: CallbackQuery) -> None:
    task_key = cb.data.split(":", 1)[1]

    async with async_session_maker() as session:
        user = await upsert_user(
            session,
            cb.from_user.id,
            cb.from_user.username if cb.from_user else None,
        )
        task = await get_task_by_key(session, task_key)

        if not task:
            await cb.answer("Görev bulunamadı.", show_alert=True)
            return

        if task.type != "telegram_auto":
            await cb.answer("Bu görev otomatik kontrol değil.", show_alert=True)
            return

        meta = task.meta or {}
        channel_id = meta.get("channel_id")
        channel_username = meta.get("channel")

    if isinstance(channel_username, str) and channel_username and not channel_username.startswith("@"):
        channel_username = "@" + channel_username

    if not channel_id and not channel_username:
        await cb.answer("Kanal bilgisi ayarlı değil (placeholder).", show_alert=True)
        return

    chat = channel_id or channel_username

    try:
        member = await cb.bot.get_chat_member(chat_id=chat, user_id=cb.from_user.id)
        status = getattr(member, "status", None)
    except TelegramBadRequest:
        await cb.answer("Kontrol edemedim. Bot kanalda admin mi?", show_alert=True)
        return

    if status in MEMBER_OK:
        async with async_session_maker() as session:
            await upsert_auto_approved_submission(
                session,
                user_id=user.id,
                task_id=task.id,
                proof_text="auto: telegram_join",
            )
        await cb.answer("Üyelik bulundu. Görev tamamlandı.", show_alert=True)
    else:
        await cb.answer(
            "Henüz üye görünmüyorsun. Kanala katılıp tekrar dene.",
            show_alert=True,
        )
