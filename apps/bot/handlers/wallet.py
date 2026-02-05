from __future__ import annotations

import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from packages.db.repo_submissions import upsert_user
from packages.db.repo_wallet import set_wallet
from packages.db.session import async_session_maker

router = Router()

EVM_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
SOL_RE = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")


class WalletFlow(StatesGroup):
    waiting_address = State()


@router.message(Command("wallet"))
async def cmd_wallet(message: Message, state: FSMContext) -> None:
    await state.set_state(WalletFlow.waiting_address)
    await message.answer(
        "Cüzdan adresini gönder.\n\n"
        "Not: Bu bot asla seed/private key istemez.\n"
        "İptal: /cancel"
    )


@router.message(WalletFlow.waiting_address)
async def on_wallet_address(message: Message, state: FSMContext) -> None:
    addr = (message.text or "").strip()

    is_evm = bool(EVM_RE.match(addr))
    is_sol = bool(SOL_RE.match(addr))

    if not (is_evm or is_sol):
        await message.answer(
            "Adres formatı geçersiz görünüyor.\n"
            "EVM örneği: 0xabc...\n"
            "Solana örneği: 7Gg...\n\n"
            "Tekrar gönder veya /cancel."
        )
        return

    async with async_session_maker() as session:
        await upsert_user(
            session,
            message.from_user.id,
            message.from_user.username if message.from_user else None,
        )
        ok, msg = await set_wallet(session, message.from_user.id, addr, allow_change=False)

    await state.clear()
    await message.answer(msg)
