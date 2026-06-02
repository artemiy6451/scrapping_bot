import re

from playwright.async_api import Locator, Page

from app.parser import CommentParser
from app.telegram.schemas import TelegramComment, TelegramPost, TelegramPostWithID

COMMENTS_COUNT_TRASHOLD = 10


class TelegramCommentParser(CommentParser):
    def __init__(self, page: Page) -> None:
        self.page = page

    async def get_comments_from_post(
        self, post: TelegramPostWithID
    ) -> list[TelegramComment]:
        if post.comments_count <= COMMENTS_COUNT_TRASHOLD:
            return []
        raw_comments = await self.__get_raw_comments(post)
        comments = await self.__parse_comments(post, raw_comments)
        return comments

    async def __get_raw_comments(self, post: TelegramPost) -> list[Locator]:
        pattern = r"(?:https?://)?(?:t\.me|telegram\.me)/([a-zA-Z0-9_]+)/(\d+)$"
        match = re.search(pattern, post.link)
        if match:
            domain = match.group(1)
            message_id = match.group(2)
        else:
            return []
        link = f"https://web.telegram.org/a/#?tgaddr=tg%3A%2F%2Fresolve%3Fdomain%3D{domain}%26post%3D{message_id}"
        await self.page.goto(link, wait_until="domcontentloaded")
        await self.page.wait_for_timeout(15000)
        await self.page.locator(
            f"#message-{message_id} > .message-content-wrapper >"
            ".message-content > .CommentButton"
        ).click(timeout=2000)
        await self.page.get_by_role("button", name="Go to bottom").click()
        await self.page.pause()
        return []

    async def __parse_comments(
        self, post: TelegramPostWithID, raw_comments: list[Locator]
    ) -> list[TelegramComment]:
        return []
