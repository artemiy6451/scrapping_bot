import asyncio

from loguru import logger
from playwright.async_api import Error, Locator, Page

from app.parser import PostParser
from app.telegram.parsers.comment import TelegramCommentParser
from app.telegram.schemas import TelegramPost
from app.telegram.service import TelegramCommentService, TelegramPostService

COMMENTS_COUNT_TRASHOLD = 10


class TelegramPostParser(PostParser):
    def __init__(self, page: Page, step: int = 10) -> None:
        self.page = page
        self.step = step
        self.comment_service = TelegramCommentService()
        self.comment_parser = TelegramCommentParser(page=page)
        self.post_service = TelegramPostService()

    async def get_posts(self) -> list[TelegramPost]:
        logger.debug("Get post func started")
        channels = await self.__get_all_channels()
        channels_count = len(channels)
        posts: list[TelegramPost] = []
        for index, channel in enumerate(channels):
            await channel.click()
            await self.page.wait_for_load_state("domcontentloaded")

            logger.debug(f"Checking {index + 1}/{channels_count} channel...")

            for step in range(self.step):
                logger.debug(f"Parsing step: {step + 1}")
                posts.extend(await self.__process_channel(channel))

            break

        return posts

    async def __get_all_channels(self) -> list[Locator]:
        logger.debug("Get all channels func started")
        await self.page.get_by_text("Folder-vkzxc").first.click()

        await self.page.wait_for_timeout(10000)
        return await self.page.locator(
            ".chat-list.custom-scroll.Transition_slide.no-overscroll."
            "Transition_slide-active > div > .ListItem"
        ).all()

    async def __process_channel(self, channel: Locator) -> list[TelegramPost]:
        logger.debug("Get all channels func started")
        try:
            await channel.get_by_role("button", name="Go to bottom").click(timeout=300)
            logger.debug("Click to bottom button.")
        except Error:
            pass

        await asyncio.sleep(5)
        post_container = self.page.locator(".messages-container").first
        raw_posts = await post_container.locator(".message-content").all()
        return await self.__process_posts(raw_posts[::-1][1:])

    async def __process_posts(self, raw_posts: list[Locator]) -> list[TelegramPost]:
        logger.debug("Process posts func started")
        posts: list[TelegramPost] = []
        for raw_post in raw_posts:
            logger.debug(f"Parsing post: {raw_post}")
            comments_count = await self.__get_comments_count(raw_post)
            post_text = await self.__get_text(raw_post)
            if comments_count <= COMMENTS_COUNT_TRASHOLD:
                continue
            if post_text == "":
                continue
            post = await self.post_service.add_post(
                TelegramPost(
                    group_name=await self.__get_group_name(),
                    text=post_text,
                    comments_count=comments_count,
                    link=await self.__get_link(raw_post),
                )
            )
            if post is None:
                continue

            await self.comment_parser.get_comments_from_post(post)

        return posts

    async def __get_group_name(self) -> str:
        logger.debug("Get group name func started")
        return await self.page.title()

    async def __get_text(self, post: Locator) -> str:
        logger.debug("Get text func started")
        try:
            await post.click(button="right", timeout=500)
            await self.page.get_by_role("menuitem", name="Copy Text").click(timeout=500)
            await self.page.wait_for_timeout(1000)
            return str(await self.page.evaluate("() => navigator.clipboard.readText()"))
        except Error:
            logger.warning("No text found!")
            return ""

    async def __get_comments_count(self, post: Locator) -> int:
        logger.debug("Get comments count func started")
        try:
            comments_count = await post.locator(
                ".CommentButton > .label > span"
            ).text_content(timeout=2000)
            if comments_count is None:
                return 0
            return int(comments_count.replace("comments", "").strip())
        except Error:
            logger.warning("No comments count found!")
            return 0

    async def __get_link(self, post: Locator) -> str:
        logger.debug("Get link func started")
        try:
            await post.click(button="right", timeout=500)
            await self.page.get_by_role("menuitem", name="Copy Message Link").click(
                timeout=500
            )
            await self.page.wait_for_timeout(1000)
            return str(await self.page.evaluate("() => navigator.clipboard.readText()"))
        except Exception:
            logger.warning("No link found!")
            return ""
