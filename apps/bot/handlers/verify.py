from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from packages.db.repo_submissions import (
    create_or_update_pending_submission,
    get_task_by_key,
    upsert_user,
)
from packages.db.session import async_session_maker

router = Router()


class VerifyFlow(StatesGroup):
    waiting_proof = State()


@router.message(Command("verify"))
async def cmd_verify(message: Message) -> None:
    await message.answer(
        "Kanıt göndermek için /tasks üzerinden bir görev seç "
        "ve 'Kanıt Gönder' butonuna bas."
    )


@router.callback_query(F.data.startswith("proof:"))
async def cb_proof_start(cb: CallbackQuery, state: FSMContext) -> None:
    task_key = cb.data.split(":", 1)[1]
    await state.update_data(task_key=task_key)
    await state.set_state(VerifyFlow.waiting_proof)

    await cb.message.answer(
        "Kanıtını gönder\n\n"
        "- Link (tweet linki vb.)\n"
        "- veya kısa açıklama (Discord username gibi)\n\n"
        "İptal: /cancel"
    )
    await cb.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("İşlem iptal edildi. /tasks ile devam edebilirsin.")


@router.message(VerifyFlow.waiting_proof)
async def on_proof(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    task_key = data.get("task_key")
    proof_text = message.text

    if not task_key:
        await state.clear()
        await message.answer("Bir şeyler karıştı. /tasks üzerinden tekrar dene.")
        return

    async with async_session_maker() as session:
        user = await upsert_user(
            session,
            message.from_user.id,
            message.from_user.username if message.from_user else None,
        )
        task = await get_task_by_key(session, task_key)
        if not task:
            await message.answer("Görev bulunamadı veya aktif değil. /tasks")
            await state.clear()
            return

        await create_or_update_pending_submission(
            session,
            user_id=user.id,
            task_id=task.id,
            proof_text=proof_text,
        )

    await state.clear()
    await message.answer("Kanıt alındı. İnceleme kuyruğuna eklendi.")
