import asyncio

from loguru import logger

from app.telegram.runner import run_telegram_scraper
from app.vk.runner import run_vk_scraper


async def main() -> None:
    """
    Запускает скраперы VK и Telegram параллельно.
    Использует asyncio.gather для одновременного выполнения.
    """
    logger.info("Starting all web scrappers...")

    # Запускаем оба скрапера параллельно
    await asyncio.gather(
        run_vk_scraper(),
        run_telegram_scraper(),
    )

    logger.info("All scrappers completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
