from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar

from app.schemas import Comment, Post

T = TypeVar("T", bound=Post)


class Parser(Generic[T], ABC):

    @abstractmethod
    async def get_posts(self) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    async def get_comments_from_post(self, post: T) -> Sequence[Comment]:
        raise NotImplementedError
