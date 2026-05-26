import uuid

from pydantic import BaseModel


class CommentForModeration(BaseModel):
    comment_id: uuid.UUID

    group_name: str

    post_text: str

    comment_text: str

    link: str
