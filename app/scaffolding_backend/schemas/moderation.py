from pydantic import BaseModel


class CreateModerationLabel(BaseModel):
    comment_id: int

    label: str

    moderator_note: str | None = None

    moderator_name: str
