from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.common.config import settings
from packages.common.referral import make_ref_code
from packages.db.models import Task, TaskSubmission, User
from packages.db.repo_referrals import maybe_award_referral_bonus


async def get_task_by_key(session: AsyncSession, key: str) -> Task | None:
    return await session.scalar(
        select(Task).where(Task.key == key, Task.is_active == True)
    )


async def get_user_by_tg(session: AsyncSession, telegram_user_id: int) -> User | None:
    return await session.scalar(
        select(User).where(User.telegram_user_id == telegram_user_id)
    )


async def upsert_user(
    session: AsyncSession, telegram_user_id: int, username: str | None
) -> User:
    user = await get_user_by_tg(session, telegram_user_id)
    if user:
        user.username = username
        if not user.ref_code:
            user.ref_code = make_ref_code(user.telegram_user_id)
        await session.commit()
        return user

    user = User(telegram_user_id=telegram_user_id, username=username)
    user.ref_code = make_ref_code(user.telegram_user_id)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_or_update_pending_submission(
    session: AsyncSession,
    user_id: int,
    task_id: int,
    proof_text: str | None = None,
    proof_file_url: str | None = None,
) -> TaskSubmission:
    existing = await session.scalar(
        select(TaskSubmission).where(
            TaskSubmission.user_id == user_id,
            TaskSubmission.task_id == task_id,
        )
    )
    if existing:
        existing.status = "pending"
        existing.proof_text = proof_text
        existing.proof_file_url = proof_file_url
        await session.commit()
        return existing

    sub = TaskSubmission(
        user_id=user_id,
        task_id=task_id,
        status="pending",
        proof_text=proof_text,
        proof_file_url=proof_file_url,
    )
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub


async def upsert_auto_approved_submission(
    session: AsyncSession,
    user_id: int,
    task_id: int,
    proof_text: str,
) -> TaskSubmission:
    existing = await session.scalar(
        select(TaskSubmission).where(
            TaskSubmission.user_id == user_id,
            TaskSubmission.task_id == task_id,
        )
    )
    if existing:
        existing.status = "approved"
        existing.proof_text = proof_text
        existing.reviewed_by = None
        await session.commit()
        await maybe_award_referral_bonus(
            session, existing.user_id, settings.referral_bonus_points
        )
        return existing

    sub = TaskSubmission(
        user_id=user_id,
        task_id=task_id,
        status="approved",
        proof_text=proof_text,
        reviewed_by=None,
    )
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    await maybe_award_referral_bonus(
        session, sub.user_id, settings.referral_bonus_points
    )
    return sub


async def list_pending_submissions(
    session: AsyncSession, limit: int = 20
) -> list[tuple[TaskSubmission, User, Task]]:
    q = (
        select(TaskSubmission, User, Task)
        .join(User, User.id == TaskSubmission.user_id)
        .join(Task, Task.id == TaskSubmission.task_id)
        .where(TaskSubmission.status == "pending")
        .order_by(TaskSubmission.created_at.asc())
        .limit(limit)
    )
    res = await session.execute(q)
    return list(res.all())


async def set_submission_status(
    session: AsyncSession,
    submission_id: int,
    status: str,
    reviewed_by: int | None = None,
) -> bool:
    sub = await session.scalar(
        select(TaskSubmission).where(TaskSubmission.id == submission_id)
    )
    if not sub:
        return False
    sub.status = status
    sub.reviewed_by = reviewed_by
    await session.commit()
    if status == "approved":
        await maybe_award_referral_bonus(
            session, sub.user_id, settings.referral_bonus_points
        )
    return True
