from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from packages.common.config import settings
from packages.common.mask import mask_wallet
from packages.db.repo_referrals import get_user_by_ref_code
from packages.db.repo_submissions import upsert_user
from packages.db.repo_wallet import get_wallet_address
from packages.db.session import async_session_maker

router = Router()


@router.message(Command("start_legacy"))
async def cmd_start_legacy(message: Message) -> None:
    await message.answer("Legacy akış. Yeni başlangıç için /start kullanın.")


@router.message(Command("help_legacy"))
async def cmd_help_legacy(message: Message) -> None:
    text = (
        "Yardım\n\n"
        "Bu bot airdrop görevlerini tamamlamanı, durumunu takip etmeni "
        "ve puan kazanmanı sağlar.\n\n"
        "Komutlar:\n"
        "/start - Başlat\n"
        "/tasks - Görevler\n"
        "/verify - Kanıt gönder\n"
        "/me - Profil ve puan\n"
        "/top - Leaderboard\n"
        "/help - Yardım\n"
        "/cancel - İptal\n\n"
        "Güvenlik Notu\n"
        "Bu bot SİZDEN ASLA seed phrase / private key / şifre istemez.\n"
        "Bunları isteyen biri varsa dolandırıcılıktır, sakın paylaşma."
    )
    await message.answer(text)


@router.callback_query(F.data == "go:wallet")
async def cb_go_wallet(cb, state):
    from apps.bot.handlers.wallet import cmd_wallet

    await cb.answer()
    await cmd_wallet(cb.message, state)


@router.callback_query(F.data == "go:tasks")
async def cb_go_tasks(cb):
    await cb.answer()
    await cb.message.answer("/tasks")


@router.callback_query(F.data == "go:me")
async def cb_go_me(cb):
    await cb.answer()
    await cb.message.answer("/me")


@router.callback_query(F.data == "noop:wallet")
async def cb_noop_wallet(cb):
    tg_id = cb.from_user.id if cb.from_user else None
    if not tg_id:
        await cb.answer("Cüzdan bilgisi bulunamadı.", show_alert=True)
        return

    async with async_session_maker() as session:
        wallet = await get_wallet_address(session, tg_id)

    if wallet:
        await cb.answer(f"✅ Bağlı: {mask_wallet(wallet)}", show_alert=True)
    else:
        await cb.answer("Cüzdan bağlı görünmüyor. /wallet ile bağlayabilirsin.", show_alert=True)
