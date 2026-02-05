from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from packages.common.queue import enqueue_dm
from packages.db.models import ReferralReward, TaskSubmission, User


async def get_user_by_ref_code(session: AsyncSession, ref_code: str) -> User | None:
    return await session.scalar(select(User).where(User.ref_code == ref_code))


async def maybe_award_referral_bonus(
    session: AsyncSession, referred_user_id: int, bonus_points: int
) -> int:
    """
    referred_user_id: B (ref edilen)
    B şartları sağlıyorsa, A'ya bonus yazar.
    Returns: awarded points (0 or bonus_points)
    """
    referred = await session.get(User, referred_user_id)
    if not referred or not referred.referred_by_user_id:
        return 0

    if not getattr(referred, "wallet_address", None):
        return 0

    approved_count = await session.scalar(
        select(func.count(TaskSubmission.id)).where(
            TaskSubmission.user_id == referred_user_id,
            TaskSubmission.status == "approved",
        )
    )
    if not approved_count:
        return 0

    referrer_id = referred.referred_by_user_id
    reward = ReferralReward(
        referrer_user_id=referrer_id,
        referred_user_id=referred_user_id,
        points=bonus_points,
    )
    session.add(reward)
    try:
        await session.commit()
        referrer = await session.get(User, referrer_id)
        referred_name = (
            f"@{referred.username}"
            if referred.username
            else f"User {str(referred.telegram_user_id)[-4:]}"
        )
        if referrer:
            await enqueue_dm(
                user_id=referrer.telegram_user_id,
                message_text=(
                    f"Referral bonus kazandın: +{bonus_points}⭐\n\n"
                    f"{referred_name} ilk görevini tamamladı.\n\n"
                    "Yeni davet linkini görmek için: /me"
                ),
                parse_mode=None,
            )
        return bonus_points
    except IntegrityError:
        await session.rollback()
        return 0
