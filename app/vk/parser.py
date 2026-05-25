import asyncio

from loguru import logger
from playwright.async_api import Error, Locator, Page

from app.parser import Parser
from app.vk.schemas import VKComment, VKPost, VKPostWithID


class VKParser(Parser):
    def __init__(self, page: Page, step: int = 10) -> None:
        self.page = page
        self.step = step

    async def get_posts(self) -> list[VKPost]:
        logger.debug("Starting parse articles...")
        posts: list[VKPost] = []

        for step in range(self.step):
            logger.debug(f"Step: {step + 1}/{self.step}")

            raw_posts = await self.__get_raw_posts()

            posts.extend(await self.__parse_articles(raw_posts))
            logger.debug(f"Now articles {len(posts)}")

            await self.__scroll_page()
            logger.debug("Appended all articles from step.")

        logger.debug("All step comleated.")
        return posts

    async def get_comments_from_post(self, post: VKPostWithID) -> list[VKComment]:
        raw_comments = await self.__get_raw_comments(post)
        comments = await self.__parse_comments(post, raw_comments)
        return comments

    async def __parse_comments(
        self, post: VKPostWithID, raw_comments: list[Locator]
    ) -> list[VKComment]:
        comments: list[VKComment] = []

        for index, comment in enumerate(raw_comments):
            logger.debug(f"Parsing post {index + 1}/{len(raw_comments)}")
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
        logger.debug(f"Opening page: {post.link}")
        await self.page.goto(post.link, wait_until="load")
        await asyncio.sleep(2)
        raw_comments: list[Locator] = await self.page.get_by_test_id(
            "wall_comments_comment_root"
        ).all()
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

    async def __get_raw_posts(self) -> list[Locator]:
        logger.debug("Starting scrapping VK feed page.")

        feed = self.page.get_by_role("feed").first

        return await feed.get_by_role("article").all()

    async def __scroll_page(self) -> None:
        await self.page.evaluate("window.scrollBy(0, 6000)")
        logger.debug("Page scrolled.")
        await self.page.wait_for_timeout(2000)

    async def __parse_articles(self, raw_posts: list[Locator]) -> list[VKPost]:
        posts: list[VKPost] = []

        for raw_post in raw_posts:
            group_name = await self.__get_group_name(raw_post)

            if group_name == "":
                continue

            posts.append(
                VKPost(
                    group_name=group_name,
                    text=await self.__get_text(raw_post),
                    likes=await self.__get_likes(raw_post),
                    comments_count=await self.__get_comments_count(raw_post),
                    share=await self.__get_share_count(raw_post),
                    link=await self.__get_post_link(raw_post),
                )
            )
        return posts

    async def __get_group_name(self, locator: Locator) -> str:
        try:
            return await locator.get_by_test_id(
                "post-header-title",
            ).inner_text(timeout=1500)
        except Error:
            return ""

    async def __get_text(self, locator: Locator) -> str:
        try:
            return await locator.locator("[data-testid='showmoretext']").inner_text(
                timeout=1500
            )
        except Error:
            return ""

    async def __get_likes(self, locator: Locator) -> int:
        try:
            raw_likes = await locator.get_by_test_id(
                "post_footer_action_like"
            ).inner_text(timeout=1500)
            if raw_likes == "":
                return 0
            likes = int(float(raw_likes.replace("K", "").replace(",", ".")) * 1000)
            return likes
        except Error:
            return 0

    async def __get_comments_count(self, locator: Locator) -> int:
        try:
            raw_comments = await locator.get_by_test_id(
                "post_footer_action_comment"
            ).inner_text(timeout=1500)
            if raw_comments == "":
                return 0
            comments = int(float(raw_comments.replace("K", "").replace(",", ".")) * 1000)
            return comments
        except Error:
            return 0

    async def __get_share_count(self, locator: Locator) -> int:
        try:
            raw_share = await locator.get_by_test_id(
                "post_footer_action_share"
            ).inner_text(timeout=1500)
            if raw_share == "":
                return 0
            share = int(float(raw_share.replace("K", "").replace(",", ".")) * 1000)
            return share
        except Error:
            return 0

    async def __get_post_link(self, locator: Locator) -> str:
        try:
            post_link = await locator.get_by_test_id(
                "post_date_block_preview"
            ).get_attribute("href", timeout=1500)
            if post_link is None:
                return ""
            return f"https://vk.com{post_link}"
        except Error:
            return ""
