from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.scaffolding_backend.models.moderation_label import CommentModerationLabel
from app.vk.models import VKCommentModel


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_next_unlabeled(
        self,
    ) -> VKCommentModel | None:
        stmt = (
            select(VKCommentModel)
            .options(joinedload(VKCommentModel.post))
            .where(VKCommentModel.moderation_label == None)  # noqa: E711
            .limit(1)
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def create_label(
        self,
        label: CommentModerationLabel,
    ) -> None:
        self.session.add(label)

        await self.session.commit()
