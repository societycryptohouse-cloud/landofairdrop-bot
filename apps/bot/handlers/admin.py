from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from packages.common.config import settings
from packages.db.repo_submissions import (
    list_pending_submissions,
    set_submission_status,
)
from packages.db.session import async_session_maker

router = Router()


def is_admin(tg_id: int | None) -> bool:
    return tg_id is not None and tg_id in settings.admin_user_ids


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer("Bu komut yetkililere açık.")
        return

    async with async_session_maker() as session:
        rows = await list_pending_submissions(session, limit=10)

    if not rows:
        await message.answer("Pending yok.")
        return

    for sub, user, task in rows:
        kb = InlineKeyboardBuilder()
        kb.button(text="Onayla", callback_data=f"appr:{sub.id}")
        kb.button(text="Reddet", callback_data=f"rej:{sub.id}")

        text = (
            "Pending\n"
            f"User: @{user.username or '—'} ({user.telegram_user_id})\n"
            f"Task: {task.title} ({task.key})\n"
            f"Proof: {sub.proof_text or '—'}\n"
            f"ID: {sub.id}"
        )
        await message.answer(text, reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("appr:"))
async def cb_approve(cb: CallbackQuery) -> None:
    if not is_admin(cb.from_user.id if cb.from_user else None):
        await cb.answer("Yetkin yok.", show_alert=True)
        return

    sub_id = int(cb.data.split(":", 1)[1])
    async with async_session_maker() as session:
        ok = await set_submission_status(
            session, sub_id, "approved", reviewed_by=cb.from_user.id
        )

    await cb.answer("Onaylandı." if ok else "Bulunamadı.", show_alert=True)


@router.callback_query(F.data.startswith("rej:"))
async def cb_reject(cb: CallbackQuery) -> None:
    if not is_admin(cb.from_user.id if cb.from_user else None):
        await cb.answer("Yetkin yok.", show_alert=True)
        return

    sub_id = int(cb.data.split(":", 1)[1])
    async with async_session_maker() as session:
        ok = await set_submission_status(
            session, sub_id, "rejected", reviewed_by=cb.from_user.id
        )

    await cb.answer("Reddedildi." if ok else "Bulunamadı.", show_alert=True)
