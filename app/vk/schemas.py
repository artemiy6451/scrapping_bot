import uuid

from app.schemas import Comment, Post


class VKPost(Post):
    share: int
    likes: int


class VKPostWithID(VKPost):
    id: uuid.UUID
    parsed: bool


class VKComment(Comment[VKPostWithID]):
    likes: int
    post: VKPostWithID


class VKCommentWithID(VKComment):
    id: uuid.UUID
    label: str
