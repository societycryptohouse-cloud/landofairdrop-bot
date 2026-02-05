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
async def test_start_shows_connect_wallet_when_missing(mocker):
    """
    /start -> wallet yoksa ' Cüzdan Bağla' butonu gelmeli
    """
    from apps.bot.handlers.start import cmd_start

    session = mocker.Mock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)

    mocker.patch("apps.bot.handlers.start.async_session_maker", return_value=session)
    mocker.patch("apps.bot.handlers.start.upsert_user", new=AsyncMock())
    mocker.patch("apps.bot.handlers.start.get_wallet_address", new=AsyncMock(return_value=None))

    message = mocker.Mock()
    message.from_user = mocker.Mock(id=111, username="u1")
    message.text = "/start"
    message.answer = AsyncMock()

    await cmd_start(message)

    message.answer.assert_awaited()
    kwargs = message.answer.await_args.kwargs
    buttons = extract_buttons(kwargs.get("reply_markup"))

    assert ("Cüzdan Bağla", "go:wallet") in buttons
    assert ("Görevler", "go:tasks") in buttons
    assert ("Profil", "go:me") in buttons


@pytest.mark.anyio
async def test_start_shows_wallet_connected_when_present(mocker):
    """
    /start -> wallet varsa '✅ Cüzdan Bağlı' (noop:wallet) butonu gelmeli
    """
    from apps.bot.handlers.start import cmd_start

    session = mocker.Mock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    mocker.patch("apps.bot.handlers.start.async_session_maker", return_value=session)

    mocker.patch("apps.bot.handlers.start.upsert_user", new=AsyncMock())
    mocker.patch(
        "apps.bot.handlers.start.get_wallet_address",
        new=AsyncMock(return_value="0x1234567890abcdef1234567890abcdef12345678"),
    )

    message = mocker.Mock()
    message.from_user = mocker.Mock(id=222, username="u2")
    message.text = "/start"
    message.answer = AsyncMock()

    await cmd_start(message)

    message.answer.assert_awaited()
    kwargs = message.answer.await_args.kwargs
    buttons = extract_buttons(kwargs.get("reply_markup"))

    assert ("✅ Cüzdan Bağlı", "noop:wallet") in buttons
    assert ("Görevler", "go:tasks") in buttons
    assert ("Profil", "go:me") in buttons


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
