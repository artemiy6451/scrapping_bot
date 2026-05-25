from typing import Generic, TypeVar

from pydantic import BaseModel


class Post(BaseModel):
    group_name: str
    text: str
    likes: int
    comments_count: int
    link: str


T = TypeVar("T", bound=Post)


class Comment(BaseModel, Generic[T]):
    post: T
    author: str
    text: str
    likes: int
    author_link: str
