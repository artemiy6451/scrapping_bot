import uuid

from app.schemas import Comment, Post


class TelegramPost(Post):
    pass


class TelegramPostWithID(TelegramPost):
    id: uuid.UUID
    parsed: bool


class TelegramComment(Comment[TelegramPostWithID]):
    post: TelegramPostWithID


class TelegramCommentWithID(TelegramComment):
    id: uuid.UUID
    label: str
