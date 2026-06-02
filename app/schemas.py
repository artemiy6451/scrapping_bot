from typing import Generic, TypeVar

from pydantic import BaseModel


class Post(BaseModel):
    group_name: str
    text: str
    comments_count: int
    link: str


T = TypeVar("T", bound=Post)


class Comment(BaseModel, Generic[T]):
    post: T
    author: str
    text: str
    author_link: str
