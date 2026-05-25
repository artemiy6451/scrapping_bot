from sqlalchemy import BOOLEAN, TEXT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.vk.schemas import VKCommentWithID, VKPostWithID


class VKPostModel(Base):
    __tablename__ = "VKPosts"
    group_name: Mapped[str] = mapped_column(TEXT, nullable=False)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)
    likes: Mapped[int] = mapped_column(nullable=False)
    comments_count: Mapped[int] = mapped_column(nullable=False)
    share: Mapped[int] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(TEXT, nullable=False)
    parsed: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)

    comments: Mapped[list["VKCommentModel"]] = relationship(
        "VKCommentModel",
        back_populates="post",
        cascade="all, delete-orphan",
    )

    def to_read_model(self) -> VKPostWithID:
        return VKPostWithID(
            id=self.id,
            group_name=self.group_name,
            text=self.text,
            likes=self.likes,
            comments_count=self.comments_count,
            link=self.link,
            share=self.share,
            parsed=self.parsed,
        )


class VKCommentModel(Base):
    __tablename__ = "VKComments"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("VKPosts.id"), nullable=False, index=True
    )
    author: Mapped[str] = mapped_column(TEXT, nullable=False)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)
    likes: Mapped[int] = mapped_column(nullable=False, default=0)
    author_link: Mapped[str] = mapped_column(TEXT, nullable=False)

    post: Mapped["VKPostModel"] = relationship(
        "VKPostModel",
        back_populates="comments",
        lazy="joined",
        innerjoin=True,
    )

    def to_read_model(self) -> VKCommentWithID:
        return VKCommentWithID(
            id=self.id,
            post=self.post.to_read_model(),
            author=self.author,
            text=self.text,
            likes=self.likes,
            author_link=self.author_link,
        )
