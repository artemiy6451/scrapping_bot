from pydantic import BaseModel


class Post(BaseModel):
    group_name: str
    text: str
    likes: int
    comments: int
    link: str


class Comment(BaseModel):
    post: Post
    author: str
    text: str
    likes: int
