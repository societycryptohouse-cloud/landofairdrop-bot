from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from packages.db.repo_submissions import upsert_user
from packages.db.repo_tasks import get_tasks_header_stats, list_tasks_with_status
from packages.db.session import async_session_maker

router = Router()

STATUS_BADGE = {
    "approved": "✅ Onaylandı",
    "pending": "⏳ İncelemede",
    "rejected": "❌ Reddedildi",
    "not_started": "⚪ Başlamadın",
}


@router.message(Command("tasks"))
async def cmd_tasks(message: Message) -> None:
    async with async_session_maker() as session:
        await upsert_user(
            session,
            message.from_user.id,
            message.from_user.username if message.from_user else None,
        )
        stats = await get_tasks_header_stats(session, message.from_user.id)
        rows = await list_tasks_with_status(session, message.from_user.id)

    if not rows:
        await message.answer("Aktif görev yok.")
        return

    pending_part = f" · ⏳ {stats['pending']}" if stats["pending"] else ""
    header = (
        f"Görevler — ✅ {stats['approved']}/{stats['total']}"
        f"{pending_part} · ⭐ {stats['points']} puan"
    )
    await message.answer(header)

    for task, status, _sub in rows:
        badge = STATUS_BADGE.get(status, status)

        desc = (task.description or "").strip()
        desc_line = f"\n{desc}" if desc else ""

        text = (
            f"<b>{task.title}</b>\n"
            f"{badge} · ⭐ {task.points} puan"
            f"{desc_line}"
        )

        kb = InlineKeyboardBuilder()

        if task.type == "telegram_auto":
            if status != "approved":
                kb.button(text="Kontrol Et", callback_data=f"check:{task.key}")
        elif task.type == "proof_required":
            if status != "approved":
                kb.button(text="Kanıt Gönder", callback_data=f"proof:{task.key}")

        if status == "rejected":
            kb.button(text="Tekrar Dene", callback_data=f"proof:{task.key}")

        await message.answer(text, reply_markup=kb.as_markup())


@router.message(Command("verify"))
async def cmd_verify(message: Message) -> None:
    text = (
        "Telegram görevleri otomatik kontrol edilir.\n"
        "X/Discord için kanıt linkini gönder veya açıklama yaz.\n"
        "Kanıtın inceleme kuyruğuna eklenecek."
    )
    await message.answer(text)
