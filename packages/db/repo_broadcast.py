from __future__ import annotations

from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import TaskSubmission, User


async def list_broadcast_user_ids(session: AsyncSession, segment: str) -> list[int]:
    segment = (segment or "all").lower()

    if segment == "all":
        rows = await session.execute(select(User.telegram_user_id))
        return [r[0] for r in rows.all()]

    if segment == "wallet":
        rows = await session.execute(
            select(User.telegram_user_id).where(User.wallet_address.isnot(None))
        )
        return [r[0] for r in rows.all()]

    if segment == "pending":
        rows = await session.execute(
            select(distinct(User.telegram_user_id))
            .select_from(TaskSubmission)
            .join(User, User.id == TaskSubmission.user_id)
            .where(TaskSubmission.status == "pending")
        )
        return [r[0] for r in rows.all()]

    rows = await session.execute(select(User.telegram_user_id))
    return [r[0] for r in rows.all()]
