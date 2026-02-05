from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import ReferralReward, Task, TaskSubmission, User


async def get_profile_stats(session: AsyncSession, telegram_user_id: int):
    user = await session.scalar(
        select(User).where(User.telegram_user_id == telegram_user_id)
    )
    if not user:
        return None

    approved_points = await session.scalar(
        select(func.coalesce(func.sum(Task.points), 0))
        .select_from(TaskSubmission)
        .join(Task, Task.id == TaskSubmission.task_id)
        .where(
            TaskSubmission.user_id == user.id,
            TaskSubmission.status == "approved",
        )
    )

    pending_count = await session.scalar(
        select(func.count(TaskSubmission.id)).where(
            TaskSubmission.user_id == user.id,
            TaskSubmission.status == "pending",
        )
    )

    approved_count = await session.scalar(
        select(func.count(TaskSubmission.id)).where(
            TaskSubmission.user_id == user.id,
            TaskSubmission.status == "approved",
        )
    )

    ref_bonus_points = await session.scalar(
        select(func.coalesce(func.sum(ReferralReward.points), 0)).where(
            ReferralReward.referrer_user_id == user.id
        )
    )

    approved_points = int(approved_points or 0)
    ref_bonus_points = int(ref_bonus_points or 0)
    total_points = approved_points + ref_bonus_points

    return {
        "user": user,
        "approved_points": approved_points,
        "ref_bonus_points": ref_bonus_points,
        "total_points": total_points,
        "pending_count": int(pending_count or 0),
        "approved_count": int(approved_count or 0),
    }


async def get_referral_stats(session: AsyncSession, telegram_user_id: int):
    user = await session.scalar(
        select(User).where(User.telegram_user_id == telegram_user_id)
    )
    if not user:
        return {"ref_count": 0, "ref_bonus_points": 0}

    ref_count = await session.scalar(
        select(func.count(ReferralReward.id)).where(
            ReferralReward.referrer_user_id == user.id
        )
    )
    ref_bonus_points = await session.scalar(
        select(func.coalesce(func.sum(ReferralReward.points), 0)).where(
            ReferralReward.referrer_user_id == user.id
        )
    )

    return {
        "ref_count": int(ref_count or 0),
        "ref_bonus_points": int(ref_bonus_points or 0),
    }
