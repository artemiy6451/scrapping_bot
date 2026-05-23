from loguru import logger

from app.database import async_session_maker
from app.repository import SQLAlchemyRepository
from app.vk.models import VKPostModel
from app.vk.schemas import VKPost, VKPostWithID


class VKParserService:
    def __init__(self) -> None:
        self.VKPostRepository: SQLAlchemyRepository[VKPostModel] = SQLAlchemyRepository(
            async_session_maker, VKPostModel
        )

    async def find_post_by_text(self, text: str) -> VKPostWithID | None:
        post = await self.VKPostRepository.find_one(filter=(VKPostModel.text == text))
        if post is None:
            return None
        return post.to_read_model()

    async def add_posts(self, posts: list[VKPost]) -> None:
        logger.debug(f"Add {len(posts)} posts to database.")
        for index, post in enumerate(posts):
            saved_post = await self.find_post_by_text(post.text)
            if saved_post is not None:
                logger.debug(f"Post with text: {post.text} already exist.")
                continue
            if post.group_name == "":
                continue
            await self.VKPostRepository.add_one(post.model_dump())
            logger.debug(f"Added post {index + 1}/{len(posts)}")
        logger.debug("All post added.")
