from sqlalchemy import BOOLEAN, TEXT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.telegram.schemas import TelegramCommentWithID, TelegramPostWithID


class TelegramPostModel(Base):
    __tablename__ = "TelegramPosts"
    group_name: Mapped[str] = mapped_column(TEXT, nullable=False)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)
    link: Mapped[str] = mapped_column(TEXT, nullable=False)
    comments_count: Mapped[int] = mapped_column(nullable=False)

    parsed: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)

    comments: Mapped[list["TelegramCommentModel"]] = relationship(
        "TelegramCommentModel",
        back_populates="post",
        cascade="all, delete-orphan",
    )

    def to_read_model(self) -> TelegramPostWithID:
        return TelegramPostWithID(
            id=self.id,
            group_name=self.group_name,
            text=self.text,
            comments_count=self.comments_count,
            parsed=self.parsed,
            link=self.link,
        )


class TelegramCommentModel(Base):
    __tablename__ = "TelegramComments"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("TelegramPosts.id"), nullable=False, index=True
    )
    author: Mapped[str] = mapped_column(TEXT, nullable=False)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)
    author_link: Mapped[str] = mapped_column(TEXT, nullable=False)

    post: Mapped["TelegramPostModel"] = relationship(
        "TelegramPostModel",
        back_populates="comments",
        lazy="joined",
        innerjoin=True,
    )

    def to_read_model(self) -> TelegramCommentWithID:
        return TelegramCommentWithID(
            post=self.post.to_read_model(),
            author=self.author,
            text=self.text,
            author_link=self.author_link,
            id=self.id,
        )
