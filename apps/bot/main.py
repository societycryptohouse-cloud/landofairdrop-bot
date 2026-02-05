from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from packages.common.api_client import api_get
from packages.common.config import settings
from packages.common.security import is_token_match
from apps.bot.handlers.start import router as start_router
from apps.bot.handlers.tasks import router as tasks_router
from apps.bot.handlers.admin import router as admin_router
from apps.bot.handlers.verify import router as verify_router
from apps.bot.handlers.checks import router as checks_router
from apps.bot.handlers.me import router as me_router
from apps.bot.handlers.top import router as top_router
from apps.bot.handlers.broadcast import router as broadcast_router
from apps.bot.handlers.wallet import router as wallet_router
from apps.bot.handlers.tg_api import router as tg_api_router


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="daily", description="Daily menu"),
        BotCommand(command="link", description="Parent-child link"),
        BotCommand(command="status", description="Status"),
        BotCommand(command="help", description="Help"),
    ]
    await bot.set_my_commands(commands)


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start_router)
    dp.include_router(tasks_router)
    dp.include_router(verify_router)
    dp.include_router(checks_router)
    dp.include_router(me_router)
    dp.include_router(top_router)
    dp.include_router(wallet_router)
    dp.include_router(broadcast_router)
    dp.include_router(tg_api_router)
    dp.include_router(admin_router)
    return dp


async def main() -> None:
    if settings.app_env == "staging" and is_token_match(
        settings.bot_token, settings.prod_bot_token_fingerprint
    ):
        raise SystemExit("Refusing to start: staging is using PROD token.")
    if settings.app_env == "prod" and is_token_match(
        settings.bot_token, settings.staging_bot_token_fingerprint
    ):
        raise SystemExit("Refusing to start: prod is using STAGING token.")

    if not settings.api_base_url or not settings.api_key:
        raise SystemExit("API_BASE_URL / API_KEY is required.")

    # Fail fast if API is down
    await api_get("/health")

    bot = Bot(token=settings.bot_token, parse_mode=ParseMode.HTML)
    await set_commands(bot)

    dp = build_dispatcher()
    if settings.bot_mode == "polling":
        await dp.start_polling(bot)
    else:
        raise SystemExit("BOT_MODE=webhook is not implemented yet.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
