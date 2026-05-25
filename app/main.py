import asyncio

from loguru import logger
from playwright.async_api import BrowserContext, Page, Playwright, async_playwright

from app.vk.parser import VKParser
from app.vk.service import VKCommentService, VKPostService


async def create_browser_context(playwright: Playwright) -> BrowserContext:
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir="data/profile",
        headless=False,
        slow_mo=50,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    logger.debug("Browser started...")
    context.set_default_timeout(0)

    return context


async def parse_and_save_posts(
    page: Page, parser: VKParser, service: VKPostService
) -> None:
    logger.debug("Opening page...")
    await page.goto(
        "https://vk.com/feed",
        wait_until="load",
    )
    logger.debug("Page opened")

    posts = await parser.get_posts()
    logger.debug(f"Founded {len(posts)} articles.")

    await service.add_posts(posts)


async def parse_and_save_comments_from_post(
    parser: VKParser,
    post_service: VKPostService,
    comment_service: VKCommentService,
) -> None:
    logger.debug("Starting parse comments from data base posts...")
    async for post in post_service.get_post_iter():
        logger.debug(f"Found new post with link: {post.link}")
        comments = await parser.get_comments_from_post(post)

        await comment_service.add_comments(comments)


async def main() -> None:
    logger.debug("Starting VK web scrapping...")
    async with async_playwright() as p:
        context = await create_browser_context(p)

        page = await context.new_page()
        logger.debug("Created new page.")

        parser = VKParser(page=page, step=2)
        post_service = VKPostService()
        comment_service = VKCommentService()

        await parse_and_save_posts(page, parser, post_service)

        await parse_and_save_comments_from_post(parser, post_service, comment_service)

        await page.pause()

        await context.close()


if __name__ == "__main__":
    asyncio.run(main())
