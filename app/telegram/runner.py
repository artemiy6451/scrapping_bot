from loguru import logger
from playwright.async_api import BrowserContext, Page, Playwright, async_playwright

from app.telegram.parsers.comment import TelegramCommentParser
from app.telegram.parsers.post import TelegramPostParser
from app.telegram.service import TelegramCommentService, TelegramPostService


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


async def parse_and_save_posts(
    page: Page, parser: TelegramPostParser, service: TelegramPostService
) -> None:
    logger.debug("Opening page...")
    await page.goto(
        "https://web.telegram.org/",
        wait_until="load",
    )
    await page.wait_for_timeout(10000)
    logger.debug("Page opened")

    posts = await parser.get_posts()
    logger.debug(f"Founded {len(posts)} posts.")
    await service.add_posts(posts)


async def parse_and_save_comments_from_post(
    comment_parser: TelegramCommentParser,
    post_service: TelegramPostService,
    comment_service: TelegramCommentService,
) -> None:
    logger.debug("Starting parse comments from data base posts...")
    async for post in post_service.get_post_iter():
        logger.debug(f"Found new post with link: {post.link}")
        comments = await comment_parser.get_comments_from_post(post)
        if comments is None:
            continue
        await comment_service.add_comments(comments)
    logger.debug("All comments parsed.")


async def run_telegram_scraper() -> None:
    """Запускает скрапинг Telegram."""
    logger.info("Starting Telegram web scrapping...")

    async with async_playwright() as p:
        context = await create_browser_context(p)
        page = await context.new_page()
        logger.debug("Created new page.")

        post_parser = TelegramPostParser(page=page, step=20)
        # comment_parser = TelegramCommentParser(page=page)
        post_service = TelegramPostService()
        # comment_service = TelegramCommentService()

        await parse_and_save_posts(page, post_parser, post_service)
        # await parse_and_save_comments_from_post(
        # comment_parser, post_service, comment_service
        # )

        await page.pause()
        await context.close()

    logger.info("Telegram scraping completed")
