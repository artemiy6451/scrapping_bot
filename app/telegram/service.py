import csv
import uuid
from datetime import datetime
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

    async def add_post(self, post: TelegramPost) -> TelegramPostWithID | None:
        logger.debug(f"Add post: {post} to database.")
        saved_post = await self.find_post_by_text(post.text)
        if saved_post is not None:
            logger.debug(f"Post with text: {post.text} already exist.")
            return None
        if post.group_name == "":
            return None
        if post.text == "":
            return None
        new_post = await self.TelegramPostRepository.add_one(post.model_dump())
        logger.debug("Post added.")
        return new_post.to_read_model()

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

    async def add_comment(self, comment: TelegramComment) -> None:
        logger.debug(f"Add comment: {comment} to database.")
        saved_comment = await self.find_comment(comment.author, comment.text)
        if saved_comment is not None:
            logger.debug(f"Comment with text: {comment.text} already exist.")
            return None
        if comment.text == "":
            return None
        data = {
            "post_id": comment.post.id,
            "author": comment.author,
            "text": comment.text,
            "author_link": comment.author_link,
        }
        await self.TelegramCommentRepository.add_one(data)
        logger.debug("Comment added.")
        return None

    async def find_comment(self, author: str, text: str) -> TelegramCommentWithID | None:
        comment = await self.TelegramCommentRepository.find_one(
            filter=(TelegramCommentModel.author == author)
            & (TelegramCommentModel.text == text)
        )
        if comment is None:
            return None
        return comment.to_read_model()

    async def generate_comments_dataset(self) -> None:
        comments = await self.TelegramCommentRepository.find_all(limit=10**10)

        if comments is None:
            return None

        data: list[list[str | uuid.UUID]] = []
        data.append(["ID", "Post Text", "Comment Text", "Label"])

        for comment in comments:
            parsed_comment = comment.to_read_model()
            data.append(
                [
                    parsed_comment.id,
                    parsed_comment.post.text.strip().replace("\n", "").replace(",", ""),
                    parsed_comment.text.strip().replace("\n", "").replace(",", ""),
                    parsed_comment.label,
                ]
            )

        with open(
            f"data/datasets/telegram_{datetime.now()}.csv", mode="w", newline=""
        ) as file:
            writer = csv.writer(file)
            writer.writerows(data)
