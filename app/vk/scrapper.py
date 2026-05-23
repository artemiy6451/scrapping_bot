import asyncio

from loguru import logger
from playwright.async_api import async_playwright

from app.vk.parser import VKParser
from app.vk.service import VKParserService


async def main() -> None:
    logger.debug("Starting VK web scrapping...")
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="data/profile",
            headless=False,
            slow_mo=50,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        logger.debug("Browser started...")
        context.set_default_timeout(0)

        page = await context.new_page()
        logger.debug("Created new page.")

        logger.debug("Opening page...")
        await page.goto(
            "https://vk.com/feed",
            wait_until="load",
        )
        logger.debug("Page opened")

        parser = VKParser(page=page, step=2)
        posts = await parser.get_posts()
        logger.debug(f"Founded {len(posts)} articles.")

        parser_service = VKParserService()
        await parser_service.add_posts(posts)

        await page.pause()

        await context.close()


if __name__ == "__main__":
    asyncio.run(main())
