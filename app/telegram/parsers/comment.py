import asyncio
import re

from loguru import logger
from playwright.async_api import Error, Locator, Page

from app.parser import CommentParser
from app.telegram.schemas import TelegramComment, TelegramPostWithID
from app.telegram.service import TelegramCommentService


class TelegramCommentParser(CommentParser):
    def __init__(self, page: Page) -> None:
        self.page = page
        self.comment_service = TelegramCommentService()

    async def get_comments_from_post(
        self, post: TelegramPostWithID
    ) -> list[TelegramComment]:
        raw_comments = await self.__get_raw_comments(post)
        comments = await self.__parse_comments(post, raw_comments)
        await self.page.get_by_label("Back").click()
        return comments

    async def __get_raw_comments(self, post: TelegramPostWithID) -> list[Locator]:
        await self.page.wait_for_timeout(500)
        message_id = self.__get_message_id_from_link(post.link)
        await self.page.locator(
            f"#message-{message_id} > .message-content-wrapper >"
            ".message-content > .CommentButton"
        ).click()
        await asyncio.sleep(2)
        for _ in range(5):
            try:
                await self.page.get_by_role("button", name="Go to bottom").click(
                    timeout=500
                )
            except Error:
                pass

        raw_comments: list[Locator] = []
        await asyncio.sleep(3)
        step_count = len(await self.page.locator(".sender-group-container").all())
        for step in range((post.comments_count // step_count)):
            await asyncio.sleep(3)

            logger.debug(
                f"Collecting comments: {step + 1}/{(post.comments_count // step_count) + 1}. "  # noqa: E501
                f"Expecting: {post.comments_count}"
            )

            step_raw_comments = await self.page.locator(".sender-group-container").all()
            if step_count == 0:
                raw_comments.extend(step_raw_comments[1:])
            raw_comments.extend(step_raw_comments[1:])

            await step_raw_comments[0].scroll_into_view_if_needed(timeout=2000)

            # await self.page.pause()
        return raw_comments

    @staticmethod
    def __get_message_id_from_link(link: str) -> str:
        pattern = r"(?:https?://)?(?:t\.me|telegram\.me)/([a-zA-Z0-9_]+)/(\d+)$"
        match = re.search(pattern, link)
        if match:
            return match.group(2)
        else:
            return ""

    async def __parse_comments(
        self, post: TelegramPostWithID, raw_comments: list[Locator]
    ) -> list[TelegramComment]:
        comments: list[TelegramComment] = []
        for raw_comment in raw_comments:
            author = await self.__get_author_name(raw_comment)
            text = await self.__get_comment_text(raw_comment)
            author_link = await self.__get_author_link(raw_comment)

            if any((author, text, author_link)) == "":
                continue

            await self.comment_service.add_comment(
                TelegramComment(
                    post=post,
                    author=await self.__get_author_name(raw_comment),
                    text=await self.__get_comment_text(raw_comment),
                    author_link=await self.__get_author_link(raw_comment),
                )
            )

        return comments

    async def __get_author_name(self, raw_comment: Locator) -> str:
        logger.debug("Starting get author name func")
        try:
            author_name = await raw_comment.locator(".sender-title").text_content(
                timeout=10000
            )
            if author_name is None:
                raise Error(message="No author name")
            return author_name
        except Error:
            logger.warning("Failed to get author name!")
            return ""

    async def __get_comment_text(self, raw_comment: Locator) -> str:
        logger.debug("Starting get comment text func")
        try:
            comment_text = await raw_comment.locator(".text-content").text_content(
                timeout=1000
            )
            if comment_text is None:
                raise Error(message="No comment text")
            return comment_text
        except Error:
            logger.warning("Failed to get comment text!")
            return ""

    async def __get_author_link(self, raw_comment: Locator) -> str:
        logger.debug("Starting get author link func")
        try:
            author_link = await raw_comment.locator(".Avatar").get_attribute(
                "data-peer-id", timeout=1000
            )
            if author_link is None:
                raise Error(message="No author name")
            return author_link
        except Error:
            logger.warning("Failed to get author link!")
            return ""
