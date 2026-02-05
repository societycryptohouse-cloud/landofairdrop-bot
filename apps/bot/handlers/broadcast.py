from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select

from packages.common.config import settings
from packages.common.queue import enqueue_broadcast
from packages.db.models import User
from packages.db.repo_broadcast import list_broadcast_user_ids
from packages.db.session import async_session_maker

router = Router()


class BroadcastFlow(StatesGroup):
    waiting_text = State()


def is_admin(tg_id: int | None) -> bool:
    return tg_id is not None and tg_id in settings.admin_user_ids


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer("Yetkin yok.")
        return
    parts = (message.text or "").split(maxsplit=1)
    segment = parts[1].strip().lower() if len(parts) > 1 else "all"

    await state.update_data(segment=segment)
    await state.set_state(BroadcastFlow.waiting_text)
    await message.answer(
        f"Broadcast mesajını gönder.\n"
        f"Hedef segment: {segment}\n"
        f"İptal: /cancel"
    )


@router.message(BroadcastFlow.waiting_text)
async def on_broadcast_text(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await state.clear()
        return

    text = (message.text or "").strip()
    if not text:
        await message.answer("Mesaj boş olamaz.")
        return

    data = await state.get_data()
    segment = data.get("segment", "all")

    async with async_session_maker() as session:
        user_ids = await list_broadcast_user_ids(session, segment)

    await state.update_data(text=text, user_ids=user_ids)

    kb = InlineKeyboardBuilder()
    kb.button(text="Gönder", callback_data="broadcast:send")
    kb.button(text="Vazgeç", callback_data="broadcast:cancel")

    preview = (
        f"Önizleme (hedef: {len(user_ids)} kişi, segment: {segment}):\n\n"
        f"{text}\n\n"
        "Göndereyim mi?"
    )
    await message.answer(preview, reply_markup=kb.as_markup())


@router.callback_query(F.data == "broadcast:cancel")
async def cb_broadcast_cancel(cb: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(cb.from_user.id if cb.from_user else None):
        await cb.answer("Yetkin yok.", show_alert=True)
        return
    await state.clear()
    await cb.message.answer("İptal edildi.")
    await cb.answer()


@router.callback_query(F.data == "broadcast:send")
async def cb_broadcast_send(cb: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(cb.from_user.id if cb.from_user else None):
        await cb.answer("Yetkin yok.", show_alert=True)
        return

    data = await state.get_data()
    text = data.get("text")
    user_ids = data.get("user_ids", [])
    segment = data.get("segment", "all")
    await state.clear()

    if not text:
        await cb.message.answer("Mesaj boş.")
        await cb.answer()
        return

    await enqueue_broadcast(
        {"message_text": text, "user_ids": user_ids, "parse_mode": None}
    )
    await cb.message.answer(
        f"Kuyruğa eklendi. Segment: {segment} • Hedef: {len(user_ids)} kullanıcı."
    )
    await cb.answer()
