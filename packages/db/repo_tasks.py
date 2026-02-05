from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import Task, TaskSubmission, User


async def list_active_tasks(session: AsyncSession):
    res = await session.execute(
        select(Task).where(Task.is_active == True).order_by(Task.id.asc())
    )
    return res.scalars().all()


async def list_tasks_with_status(session: AsyncSession, telegram_user_id: int):
    user = await session.scalar(
        select(User).where(User.telegram_user_id == telegram_user_id)
    )
    tasks = (
        await session.execute(
            select(Task).where(Task.is_active == True).order_by(Task.id.asc())
        )
    ).scalars().all()

    if not user:
        return [(t, "not_started", None) for t in tasks]

    subs = (
        await session.execute(
            select(TaskSubmission).where(TaskSubmission.user_id == user.id)
        )
    ).scalars().all()

    sub_by_task = {s.task_id: s for s in subs}

    result = []
    for t in tasks:
        s = sub_by_task.get(t.id)
        status = s.status if s else "not_started"
        result.append((t, status, s))
    return result


async def get_tasks_header_stats(session: AsyncSession, telegram_user_id: int):
    total_tasks = await session.scalar(
        select(func.count(Task.id)).where(Task.is_active == True)
    )

    user = await session.scalar(
        select(User).where(User.telegram_user_id == telegram_user_id)
    )
    if not user:
        return {"total": int(total_tasks or 0), "approved": 0, "pending": 0, "points": 0}

    approved = await session.scalar(
        select(func.count(TaskSubmission.id)).where(
            TaskSubmission.user_id == user.id,
            TaskSubmission.status == "approved",
        )
    )
    pending = await session.scalar(
        select(func.count(TaskSubmission.id)).where(
            TaskSubmission.user_id == user.id,
            TaskSubmission.status == "pending",
        )
    )
    points = await session.scalar(
        select(func.coalesce(func.sum(Task.points), 0))
        .select_from(TaskSubmission)
        .join(Task, Task.id == TaskSubmission.task_id)
        .where(
            TaskSubmission.user_id == user.id,
            TaskSubmission.status == "approved",
        )
    )

    return {
        "total": int(total_tasks or 0),
        "approved": int(approved or 0),
        "pending": int(pending or 0),
        "points": int(points or 0),
    }
