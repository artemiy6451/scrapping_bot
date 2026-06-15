import asyncio

from loguru import logger
from playwright.async_api import Error, Locator, Page

from app.parser import CommentParser
from app.vk.schemas import VKComment, VKPost, VKPostWithID


class VKCommentParser(CommentParser):
    def __init__(self, page: Page) -> None:
        self.page = page

    async def get_comments_from_post(self, post: VKPostWithID) -> list[VKComment]:
        raw_comments = await self.__get_raw_comments(post)
        comments = await self.__parse_comments(post, raw_comments)
        return comments

    async def __parse_comments(
        self, post: VKPostWithID, raw_comments: list[Locator]
    ) -> list[VKComment]:
        comments: list[VKComment] = []
        logger.debug(f"Expected comments: {post.comments_count}...")

        for index, comment in enumerate(raw_comments):
            logger.debug(f"Parsing comment {index + 1}/{len(raw_comments)}")
            text = await self.__get_comment_text(comment)
            if text == "":
                continue

            comments.append(
                VKComment(
                    post=post,
                    author=await self.__get_comment_author_name(comment),
                    text=await self.__get_comment_text(comment),
                    likes=await self.__get_comment_likes(comment),
                    author_link=await self.__get_comment_author_link(comment),
                )
            )

        return comments

    async def __get_raw_comments(self, post: VKPost) -> list[Locator]:
        if post.link == "":
            return []
        logger.debug(f"Opening page: {post.link}")
        await self.page.goto(post.link, wait_until="load")
        await asyncio.sleep(2)

        previous_comment_count = 0
        for step in range(50):
            logger.debug(f"Trying load comment: {step + 1}/{50}")
            current_comment_count = await self.page.get_by_test_id(
                "wall_comments_comment_root"
            ).count()

            if current_comment_count == previous_comment_count:
                logger.debug("All comments loaded.")
                break

            previous_comment_count = current_comment_count

            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            try:
                await self.page.wait_for_load_state("networkidle", timeout=10000)
            except Error:
                pass

        while True:
            buttons = await self.page.get_by_test_id("show_next_comments").all()
            if not buttons:
                break

            for _ in range(5):
                await buttons[0].click(timeout=500)
                logger.debug("Open more comments on page")

            try:
                await self.page.wait_for_load_state("networkidle", timeout=5000)
            except Error:
                pass

        root_comments: list[Locator] = await self.page.get_by_test_id(
            "wall_comments_comment_root"
        ).all()

        threads_comments = await self.page.get_by_test_id(
            "wall_comments_comment_in_thread"
        ).all()

        raw_comments = root_comments + threads_comments

        logger.debug(f"Found {len(raw_comments)} comments.")
        return raw_comments

    async def __get_comment_author_link(self, locator: Locator) -> str:
        try:
            author_link = await locator.get_by_test_id("comment-avatar").get_attribute(
                "href"
            )
            if author_link is None:
                return ""
            return f"https://vk.com{author_link}"
        except Error:
            return ""

    async def __get_comment_likes(self, locator: Locator) -> int:
        try:
            raw_likes = await locator.get_by_test_id("comment-like").inner_text(
                timeout=1500
            )
            if raw_likes is None or raw_likes == "":
                return 0
            else:
                return int(raw_likes)
        except Error:
            return 0

    async def __get_comment_text(self, locator: Locator) -> str:
        try:
            text = await locator.get_by_test_id("comment-text").inner_text(timeout=1500)
            if text is None:
                return ""
            return text
        except Error:
            return ""

    async def __get_comment_author_name(self, locator: Locator) -> str:
        try:
            author = await locator.get_by_test_id("comment-owner").inner_text(
                timeout=1500
            )
            if author is None:
                return ""
            return author
        except Error:
            return ""
