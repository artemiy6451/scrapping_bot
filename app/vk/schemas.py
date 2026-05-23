import uuid

from app.schemas import Post


class VKPost(Post):
    share: int


class VKPostWithID(VKPost):
    id: uuid.UUID
