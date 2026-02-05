import pytest
from unittest.mock import AsyncMock, Mock


@pytest.mark.anyio
async def test_get_profile_stats_calculates_total_points(mocker):
    """
    approved_points + ref_bonus_points = total_points
    """
    from packages.db.repo_profile import get_profile_stats

    user = Mock()
    user.id = 10
    user.telegram_user_id = 999
    user.username = "dia_test"

    session = Mock()

    session.scalar = AsyncMock(
        side_effect=[
            user,   # user
            80,     # approved_points
            1,      # pending_count
            2,      # approved_count
            10,     # ref_bonus_points
        ]
    )

    stats = await get_profile_stats(session, telegram_user_id=999)

    assert stats is not None
    assert stats["approved_points"] == 80
    assert stats["ref_bonus_points"] == 10
    assert stats["total_points"] == 90
    assert stats["pending_count"] == 1
    assert stats["approved_count"] == 2
    assert stats["user"] is user


@pytest.mark.anyio
async def test_get_profile_stats_handles_nulls_as_zero(mocker):
    """
    DB scalar None dönerse 0'a düşmeli (coalesce gibi)
    """
    from packages.db.repo_profile import get_profile_stats

    user = Mock()
    user.id = 11
    user.telegram_user_id = 111

    session = Mock()
    session.scalar = AsyncMock(
        side_effect=[
            user,   # user
            None,   # approved_points
            None,   # pending_count
            None,   # approved_count
            None,   # ref_bonus_points
        ]
    )

    stats = await get_profile_stats(session, telegram_user_id=111)

    assert stats["approved_points"] == 0
    assert stats["ref_bonus_points"] == 0
    assert stats["total_points"] == 0
    assert stats["pending_count"] == 0
    assert stats["approved_count"] == 0


@pytest.mark.anyio
async def test_get_profile_stats_returns_none_if_user_missing(mocker):
    """
    Kullanıcı yoksa None dönmeli (mevcut davranışın buysa)
    """
    from packages.db.repo_profile import get_profile_stats

    session = Mock()
    session.scalar = AsyncMock(side_effect=[None])  # user lookup None

    stats = await get_profile_stats(session, telegram_user_id=12345)
    assert stats is None
