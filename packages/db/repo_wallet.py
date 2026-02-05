from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import User


async def set_wallet(
    session: AsyncSession,
    telegram_user_id: int,
    wallet_address: str,
    allow_change: bool = False,
) -> tuple[bool, str]:
    """
    Returns (ok, message).
    allow_change=False ise bir kez set edilince değişmez.
    """
    user = await session.scalar(
        select(User).where(User.telegram_user_id == telegram_user_id)
    )
    if not user:
        return False, "Kullanıcı bulunamadı. /start"

    current = getattr(user, "wallet_address", None)
    if current and (not allow_change) and (current.lower() != wallet_address.lower()):
        return False, "Cüzdan zaten bağlı. Değiştirmek için admin ile iletişime geç."

    user.wallet_address = wallet_address
    if hasattr(user, "wallet_verified"):
        user.wallet_verified = False

    await session.commit()
    return True, "Cüzdan bağlandı."


async def get_wallet_address(
    session: AsyncSession, telegram_user_id: int
) -> str | None:
    user = await session.scalar(
        select(User).where(User.telegram_user_id == telegram_user_id)
    )
    if not user:
        return None
    return getattr(user, "wallet_address", None)
