from abc import ABC, abstractmethod
from typing import Sequence

from app.schemas import Comment, Post


class Parser(ABC):

    @abstractmethod
    async def get_posts(self) -> Sequence[Post]:
        raise NotImplementedError

    @abstractmethod
    async def get_comments_from_post(self, post: Post) -> Sequence[Comment]:
        raise NotImplementedError
