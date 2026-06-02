import uuid
from typing import AsyncGenerator

from loguru import logger

from app.database import async_session_maker
from app.repository import SQLAlchemyRepository
from app.telegram.models import TelegramCommentModel, TelegramPostModel
from app.telegram.schemas import (
    TelegramComment,
    TelegramCommentWithID,
    TelegramPost,
    TelegramPostWithID,
)


class TelegramPostService:
    def __init__(self) -> None:
        self.TelegramPostRepository: SQLAlchemyRepository[TelegramPostModel] = (
            SQLAlchemyRepository(async_session_maker, TelegramPostModel)
        )

    async def get_post_by_id(self, id: uuid.UUID) -> TelegramPostWithID | None:
        post = await self.TelegramPostRepository.find_one(
            filter=(TelegramPostModel.id == id)
        )
        if post is None:
            return None
        return post.to_read_model()

    async def find_post_by_text(self, text: str) -> TelegramPostWithID | None:
        post = await self.TelegramPostRepository.find_one(
            filter=(TelegramPostModel.text == text)
        )
        if post is None:
            return None
        return post.to_read_model()

    async def add_posts(self, posts: list[TelegramPost]) -> None:
        logger.debug(f"Add {len(posts)} posts to database.")
        for index, post in enumerate(posts):
            saved_post = await self.find_post_by_text(post.text)
            if saved_post is not None:
                logger.debug(f"Post with text: {post.text} already exist.")
                continue
            if post.group_name == "":
                continue
            if post.text == "":
                continue
            await self.TelegramPostRepository.add_one(post.model_dump())
            logger.debug(f"Added post {index + 1}/{len(posts)}")
        logger.debug("All post added.")

    async def get_post_iter(self) -> AsyncGenerator[TelegramPostWithID]:
        async for post in self.TelegramPostRepository.get_item_iter():
            if post is None:
                continue

            if post.parsed:
                continue

            yield post.to_read_model()

            # await self.mark_post_as_parsed(post.to_read_model())

    async def mark_post_as_parsed(self, post: TelegramPostWithID) -> TelegramPostWithID:
        logger.debug(f"Makring post with id: {post.id} as parsed.")
        marked_post = await self.TelegramPostRepository.update(
            where=(TelegramPostModel.id == post.id),
            data={"parsed": True},
        )
        if marked_post is None:
            raise Exception("Post not found.")

        return marked_post.to_read_model()


class TelegramCommentService:
    def __init__(self) -> None:
        self.TelegramCommentRepository: SQLAlchemyRepository[TelegramCommentModel] = (
            SQLAlchemyRepository(async_session_maker, TelegramCommentModel)
        )

    async def add_comments(self, comments: list[TelegramComment]) -> None:
        logger.debug(f"Add {len(comments)} comments to database.")
        for index, comment in enumerate(comments):
            saved_comment = await self.find_comment(comment.author, comment.text)
            if saved_comment is not None:
                logger.debug(f"Comment with text: {comment.text} already exist.")
                continue
            if comment.text == "":
                continue
            data = {
                "post_id": comment.post.id,
                "author": comment.author,
                "text": comment.text,
                "author_link": comment.author_link,
            }
            await self.TelegramCommentRepository.add_one(data)
            logger.debug(f"Added comment {index + 1}/{len(comments)}")
        logger.debug("All comments added.")

    async def find_comment(self, author: str, text: str) -> TelegramCommentWithID | None:
        comment = await self.TelegramCommentRepository.find_one(
            filter=(TelegramCommentModel.author == author)
            & (TelegramCommentModel.text == text)
        )
        if comment is None:
            return None
        return comment.to_read_model()
