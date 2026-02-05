from __future__ import annotations

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import Task, TaskSubmission, User


async def get_leaderboard(session: AsyncSession, limit: int = 10):
    """
    Returns list of dicts: {telegram_user_id, username, points}
    Points = sum(Task.points) over approved submissions.
    """
    q = (
        select(
            User.telegram_user_id,
            User.username,
            func.coalesce(func.sum(Task.points), 0).label("points"),
        )
        .select_from(TaskSubmission)
        .join(User, User.id == TaskSubmission.user_id)
        .join(Task, Task.id == TaskSubmission.task_id)
        .where(TaskSubmission.status == "approved")
        .group_by(User.telegram_user_id, User.username)
        .order_by(desc("points"), desc(func.max(TaskSubmission.updated_at)))
        .limit(limit)
    )

    rows = (await session.execute(q)).all()
    return [
        {"telegram_user_id": tg_id, "username": username, "points": int(points or 0)}
        for (tg_id, username, points) in rows
    ]


async def get_user_rank(session: AsyncSession, telegram_user_id: int):
    """
    Optional: returns user's points and rank (dense rank).
    """
    points_subq = (
        select(
            User.telegram_user_id.label("tg_id"),
            func.coalesce(func.sum(Task.points), 0).label("points"),
        )
        .select_from(TaskSubmission)
        .join(User, User.id == TaskSubmission.user_id)
        .join(Task, Task.id == TaskSubmission.task_id)
        .where(TaskSubmission.status == "approved")
        .group_by(User.telegram_user_id)
        .subquery()
    )

    ranked = (
        select(
            points_subq.c.tg_id,
            points_subq.c.points,
            func.dense_rank().over(order_by=points_subq.c.points.desc()).label("rank"),
        )
        .subquery()
    )

    row = await session.execute(
        select(ranked.c.rank, ranked.c.points).where(
            ranked.c.tg_id == telegram_user_id
        )
    )
    r = row.first()
    if not r:
        return {"rank": None, "points": 0}
    return {"rank": int(r.rank), "points": int(r.points or 0)}
