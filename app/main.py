import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

from app.config import settings
from app.logging import setup_new_logger
from app.routers.start import start_router

setup_new_logger()

dp = Dispatcher()
dp.include_router(start_router)


async def main() -> None:
    logger.debug("Starting telegram bot")
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
