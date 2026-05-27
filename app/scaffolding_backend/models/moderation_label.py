from datetime import datetime

from sqlalchemy import TEXT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class CommentModerationLabel(Base):
    __tablename__ = "comment_moderation_labels"

    comment_id: Mapped[int] = mapped_column(
        ForeignKey("VKComments.id"),
        unique=True,
        index=True,
    )

    label: Mapped[str] = mapped_column(TEXT)

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
    )

    comment = relationship(
        "VKCommentModel",
        back_populates="moderation_label",
    )
