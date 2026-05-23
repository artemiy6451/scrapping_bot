from sqlalchemy import TEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base
from app.vk.schemas import VKPostWithID


class VKPostModel(Base):
    __tablename__ = "VKPosts"
    group_name: Mapped[str] = mapped_column(TEXT, nullable=False)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)
    likes: Mapped[int] = mapped_column(nullable=False)
    comments: Mapped[int] = mapped_column(nullable=False)
    share: Mapped[int] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(TEXT, nullable=False)

    def to_read_model(self) -> VKPostWithID:
        return VKPostWithID(
            id=self.id,
            group_name=self.group_name,
            text=self.text,
            likes=self.likes,
            comments=self.comments,
            link=self.link,
            share=self.share,
        )
