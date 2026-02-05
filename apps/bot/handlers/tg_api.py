from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from packages.common.api_client import api_post

router = Router()


class LinkFlow(StatesGroup):
    waiting_code = State()


def _build_keyboard(buttons: list[dict]) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    for b in buttons or []:
        text = b.get("text") or "Devam"
        callback = b.get("callback") or ""
        if callback:
            kb.button(text=text, callback_data=callback)
    return kb


@router.message(Command("start"))
async def cmd_start_api(message: Message) -> None:
    payload = {"telegram_id": message.from_user.id, "locale": "tr", "role": None}
    data = await api_post("/tg/start", payload)
    kb = _build_keyboard(data.get("buttons", []))
    await message.answer(data.get("message", "Hoş geldiniz."), reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("role:"))
async def cb_role_select(cb: CallbackQuery) -> None:
    role = cb.data.split(":", 1)[1]
    payload = {"telegram_id": cb.from_user.id, "locale": "tr", "role": role}
    data = await api_post("/tg/start", payload)
    kb = _build_keyboard(data.get("buttons", []))
    await cb.message.answer(data.get("message", "Rol seçildi."), reply_markup=kb.as_markup())
    await cb.answer()


@router.message(Command("daily"))
async def cmd_daily(message: Message) -> None:
    payload = {"telegram_id": message.from_user.id}
    data = await api_post("/tg/daily", payload)
    kb = _build_keyboard(data.get("buttons", []))
    await message.answer(data.get("message", "Bugünün görevleri."), reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("daily:"))
async def cb_daily(cb: CallbackQuery) -> None:
    action = cb.data.split(":", 1)[1]
    payload = {"telegram_id": cb.from_user.id, "action": action}
    data = await api_post("/tg/daily", payload)
    kb = _build_keyboard(data.get("buttons", []))
    await cb.message.answer(data.get("message", "Günlük menü."), reply_markup=kb.as_markup())
    await cb.answer()


@router.message(Command("link"))
async def cmd_link(message: Message, state: FSMContext) -> None:
    kb = InlineKeyboardBuilder()
    kb.button(text="Kod Oluştur", callback_data="link:create")
    kb.button(text="Kod Gir", callback_data="link:enter")
    await message.answer(
        "Ebeveyn kodu oluşturabilir veya mevcut kodu girebilirsiniz.",
        reply_markup=kb.as_markup(),
    )
    await state.clear()


@router.callback_query(F.data == "link:create")
async def cb_link_create(cb: CallbackQuery) -> None:
    payload = {"telegram_id": cb.from_user.id}
    data = await api_post("/tg/link/create", payload)
    msg = data.get("message", "Bağlantı kodu hazır.")
    code = data.get("code")
    ttl = data.get("ttl_seconds")
    if code:
        msg = f"{msg}\n\nKod: {code}"
    if ttl:
        msg = f"{msg}\nGeçerlilik: {ttl} sn"
    await cb.message.answer(msg)
    await cb.answer()


@router.callback_query(F.data == "link:enter")
async def cb_link_enter(cb: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(LinkFlow.waiting_code)
    await cb.message.answer("Ebeveyn kodunu girin:")
    await cb.answer()


@router.message(LinkFlow.waiting_code)
async def on_link_code(message: Message, state: FSMContext) -> None:
    code = (message.text or "").strip()
    payload = {"telegram_id": message.from_user.id, "code": code}
    data = await api_post("/tg/link/confirm", payload)
    await message.answer(data.get("message", "Bağlantı tamamlandı."))
    await state.clear()


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    payload = {"telegram_id": message.from_user.id}
    data = await api_post("/tg/status", payload)
    await message.answer(data.get("message", "Durumunuz."))


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    payload = {"telegram_id": message.from_user.id}
    data = await api_post("/tg/help", payload)
    await message.answer(data.get("message", "Yardım menüsü."))
