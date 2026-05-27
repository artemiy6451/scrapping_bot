import uuid

from pydantic import BaseModel


class CreateModerationLabel(BaseModel):
    comment_id: uuid.UUID

    label: str
