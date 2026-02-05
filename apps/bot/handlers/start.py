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


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    args = (message.text or "").split(maxsplit=1)
    ref_arg = args[1] if len(args) > 1 else None

    async with async_session_maker() as session:
        user = await upsert_user(
            session,
            message.from_user.id,
            message.from_user.username if message.from_user else None,
        )

        if ref_arg and ref_arg.startswith("ref_") and user.referred_by_user_id is None:
            ref_code = ref_arg.replace("ref_", "", 1)
            ref_user = await get_user_by_ref_code(session, ref_code)
            if ref_user and ref_user.id != user.id:
                user.referred_by_user_id = ref_user.id
                await session.commit()

        wallet = await get_wallet_address(session, message.from_user.id)

    kb = InlineKeyboardBuilder()
    if wallet:
        kb.button(text="✅ Cüzdan Bağlı", callback_data="noop:wallet")
    else:
        kb.button(text="Cüzdan Bağla", callback_data="go:wallet")
    kb.button(text="Görevler", callback_data="go:tasks")
    kb.button(text="Profil", callback_data="go:me")

    wallet_line = f"\n\nCüzdan: {mask_wallet(wallet)}" if wallet else ""
    text = (
        f"<b>{settings.bot_name}</b>\n"
        "Airdrop görevlerini tamamla, puan kazan, durumunu takip et.\n"
        f"{wallet_line}\n\n"
        "Başlamak için aşağıdan seç:"
    )
    await message.answer(text, reply_markup=kb.as_markup())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
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
