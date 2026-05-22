from loguru import logger
from playwright.async_api import Error, Locator, Page

from app.vk.schemas import VKArticle


async def scrapping_page(page: Page, step: int = 10) -> list[VKArticle]:
    logger.debug("Starting scrapping VK feed page.")
    count_step = 0
    articles: list[VKArticle] = []

    while True:
        if count_step >= step:
            break
        logger.debug(f"Step: {count_step+1}/{step}")

        feed = page.get_by_role("feed").first

        raw_articles: list[Locator] = await feed.get_by_role("article").all()
        articles.extend(await parse_articles(raw_articles))
        logger.debug(f"Now articles {len(articles)}")

        await page.evaluate("window.scrollBy(0, 6000)")
        logger.debug("Page scrolled.")

        await page.wait_for_timeout(2000)

        count_step += 1

    logger.debug("All step comleated.")
    return articles


async def parse_articles(raw_articles: list[Locator]) -> list[VKArticle]:
    logger.debug("Starting parse articles...")
    articles: list[VKArticle] = []

    for raw_article in raw_articles:
        group_name = await get_group_name(raw_article)

        if group_name == "":
            continue

        articles.append(
            VKArticle(
                group_name=group_name,
                text=await get_text(raw_article),
                likes=await get_likes(raw_article),
                comments=0,
                share=0,
                link="",
            )
        )

    logger.debug("Appended all articles from step.")
    return articles


async def get_group_name(locator: Locator) -> str:
    try:
        return await locator.get_by_test_id(
            "post-header-title",
        ).inner_text(timeout=1500)
    except Error:
        return ""


async def get_text(locator: Locator) -> str:
    try:
        return await locator.locator("[data-testid='showmoretext']").inner_text(
            timeout=1500
        )
    except Error:
        return ""


async def get_likes(locator: Locator) -> int:
    try:
        raw_likes = await locator.get_by_test_id("post_footer_action_like").inner_text(
            timeout=1500
        )
        likes = int(float(raw_likes.replace("K", "").replace(",", ".")) * 1000)
        return likes
    except Error:
        return 0
