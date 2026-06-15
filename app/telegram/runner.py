from loguru import logger
from playwright.async_api import BrowserContext, Page, Playwright, async_playwright

from app.telegram.parsers.post import TelegramPostParser


async def create_browser_context(playwright: Playwright) -> BrowserContext:
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir="data/telegram",
        headless=False,
        slow_mo=50,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    logger.debug("Browser started...")
    context.set_default_timeout(0)
    return context


async def parse_posts(page: Page, parser: TelegramPostParser) -> None:
    logger.debug("Opening page...")
    await page.goto(
        "https://web.telegram.org/",
        wait_until="load",
    )
    await page.wait_for_timeout(10000)
    logger.debug("Page opened")

    posts = await parser.get_posts()
    logger.debug(f"Founded {len(posts)} posts.")


async def run_telegram_scraper() -> None:
    """Запускает скрапинг Telegram."""
    logger.info("Starting Telegram web scrapping...")

    async with async_playwright() as p:
        context = await create_browser_context(p)
        page = await context.new_page()
        logger.debug("Created new page.")

        post_parser = TelegramPostParser(page=page, step=20)

        await parse_posts(page, post_parser)
        # cs = TelegramCommentService()
        # await cs.generate_comments_dataset()

        # await page.pause()
        await context.close()

    logger.info("Telegram scraping completed")
