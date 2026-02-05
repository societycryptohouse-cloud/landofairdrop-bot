import pytest
from unittest.mock import AsyncMock


def extract_buttons(reply_markup):
    """
    aiogram InlineKeyboardMarkup -> list of (text, callback_data)
    """
    if not reply_markup:
        return []
    rows = getattr(reply_markup, "inline_keyboard", []) or []
    out = []
    for row in rows:
        for btn in row:
            out.append((getattr(btn, "text", None), getattr(btn, "callback_data", None)))
    return out


@pytest.mark.anyio
async def test_start_api_returns_buttons(mocker):
    """
    /start -> API'den gelen butonlar gönderilmeli
    """
    from apps.bot.handlers.tg_api import cmd_start_api

    mocker.patch(
        "apps.bot.handlers.tg_api.api_post",
        new=AsyncMock(
            return_value={
                "message": "Rolünü seç",
                "buttons": [
                    {"text": "Maceracı (Çocuk)", "callback": "role:child"},
                    {"text": "Gözlemci (Ebeveyn)", "callback": "role:parent"},
                ],
            }
        ),
    )

    message = mocker.Mock()
    message.from_user = mocker.Mock(id=111, username="u1")
    message.text = "/start"
    message.answer = AsyncMock()

    await cmd_start_api(message)

    message.answer.assert_awaited()
    kwargs = message.answer.await_args.kwargs
    buttons = extract_buttons(kwargs.get("reply_markup"))

    assert ("Maceracı (Çocuk)", "role:child") in buttons
    assert ("Gözlemci (Ebeveyn)", "role:parent") in buttons


@pytest.mark.anyio
async def test_role_callback_calls_api(mocker):
    """
    role:child -> API çağrısı yapıp mesaj döndürmeli
    """
    from apps.bot.handlers.tg_api import cb_role_select

    mocker.patch(
        "apps.bot.handlers.tg_api.api_post",
        new=AsyncMock(return_value={"message": "Rol kaydedildi", "buttons": []}),
    )

    cb = mocker.Mock()
    cb.data = "role:child"
    cb.from_user = mocker.Mock(id=222)
    cb.message = mocker.Mock()
    cb.message.answer = AsyncMock()
    cb.answer = AsyncMock()

    await cb_role_select(cb)

    cb.message.answer.assert_awaited()
    cb.answer.assert_awaited()


@pytest.mark.anyio
async def test_noop_wallet_popup_shows_masked_wallet(mocker):
    """
    noop:wallet -> wallet varsa cb.answer show_alert=True ve maskeli address içermeli
    """
    from apps.bot.handlers.start import cb_noop_wallet

    session = mocker.Mock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    mocker.patch("apps.bot.handlers.start.async_session_maker", return_value=session)

    mocker.patch(
        "apps.bot.handlers.start.get_wallet_address",
        new=AsyncMock(return_value="0x1234567890abcdef1234567890abcdef12345678"),
    )
    mocker.patch("apps.bot.handlers.start.mask_wallet", return_value="0x12...5678")

    cb = mocker.Mock()
    cb.from_user = mocker.Mock(id=333)
    cb.answer = AsyncMock()

    await cb_noop_wallet(cb)

    cb.answer.assert_awaited()
    args = cb.answer.await_args.args
    kwargs = cb.answer.await_args.kwargs

    assert kwargs.get("show_alert") is True
    assert "✅ Bağlı:" in args[0]
    assert "0x12...5678" in args[0]


@pytest.mark.anyio
async def test_noop_wallet_popup_redirects_when_missing(mocker):
    """
    noop:wallet -> wallet yoksa yönlendirici mesaj dönmeli
    """
    from apps.bot.handlers.start import cb_noop_wallet

    session = mocker.Mock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    mocker.patch("apps.bot.handlers.start.async_session_maker", return_value=session)

    mocker.patch("apps.bot.handlers.start.get_wallet_address", new=AsyncMock(return_value=None))

    cb = mocker.Mock()
    cb.from_user = mocker.Mock(id=444)
    cb.answer = AsyncMock()

    await cb_noop_wallet(cb)

    cb.answer.assert_awaited()
    text = cb.answer.await_args.args[0]
    assert "/wallet" in text
