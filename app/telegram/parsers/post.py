from loguru import logger
from playwright.async_api import Error, Locator, Page

from app.parser import PostParser
from app.telegram.schemas import TelegramPost


class TelegramPostParser(PostParser):
    def __init__(self, page: Page, step: int = 10) -> None:
        self.page = page
        self.step = step

    async def get_posts(self) -> list[TelegramPost]:
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
        await self.page.get_by_text("Folder-vkzxc").first.click()

        await self.page.wait_for_timeout(10000)
        return await self.page.locator(
            ".chat-list.custom-scroll.Transition_slide.no-overscroll."
            "Transition_slide-active > div > .ListItem"
        ).all()

    async def __process_channel(self, channel: Locator) -> list[TelegramPost]:
        try:
            await channel.get_by_role("button", name="Go to bottom").click(timeout=300)
            logger.debug("Click to bottom button.")
        except Error:
            pass

        await self.page.wait_for_timeout(2000)
        post_container = self.page.locator(".messages-container").first
        raw_posts = await post_container.locator(".message-content").all()
        return await self.__process_posts(raw_posts[::-1])

    async def __process_posts(self, raw_posts: list[Locator]) -> list[TelegramPost]:
        posts: list[TelegramPost] = []
        for raw_post in raw_posts:
            posts.append(
                TelegramPost(
                    group_name=await self.__get_group_name(),
                    text=await self.__get_text(raw_post),
                    comments_count=await self.__get_comments_count(raw_post),
                    link=await self.__get_link(raw_post),
                )
            )

        return posts

    async def __get_group_name(self) -> str:
        return await self.page.title()

    async def __get_text(self, post: Locator) -> str:
        try:
            await post.click(button="right")
            await self.page.get_by_role("menuitem", name="Copy Text").click()
            await self.page.wait_for_timeout(1000)
            return str(await self.page.evaluate("() => navigator.clipboard.readText()"))
        except Error:
            return ""

    async def __get_comments_count(self, post: Locator) -> int:
        try:
            comments_count = await post.locator(
                ".CommentButton > .label > span"
            ).text_content(timeout=2000)
            if comments_count is None:
                return 0
            return int(comments_count.replace("comments", "").strip())
        except Error:
            return 0

    async def __get_link(self, post: Locator) -> str:
        try:
            await post.click(button="right")
            await self.page.get_by_role("menuitem", name="Copy Message Link").click(
                timeout=500
            )
            await self.page.wait_for_timeout(1000)
            return str(await self.page.evaluate("() => navigator.clipboard.readText()"))
        except Exception:
            return ""
