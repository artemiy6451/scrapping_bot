from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar

from app.schemas import Comment, Post

P = TypeVar("P", bound=Post)
C = TypeVar("C", bound=Comment)


class PostParser(Generic[P], ABC):
    @abstractmethod
    async def get_posts(self) -> list[P]:
        raise NotImplementedError


class CommentParser(Generic[C], ABC):
    @abstractmethod
    async def get_comments_from_post(self, post: C) -> Sequence[Comment]:
        raise NotImplementedError
