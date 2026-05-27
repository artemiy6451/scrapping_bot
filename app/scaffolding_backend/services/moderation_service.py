from app.scaffolding_backend.models.moderation_label import (
    CommentModerationLabel,
)
from app.scaffolding_backend.repositories.comments import CommentRepository
from app.scaffolding_backend.schemas.comment import CommentForModeration
from app.scaffolding_backend.schemas.moderation import CreateModerationLabel


class ModerationService:
    def __init__(self, repository: CommentRepository):
        self.repository = repository

    async def get_next_comment(
        self,
    ) -> CommentForModeration | None:
        comment = await self.repository.get_next_unlabeled()

        if comment is None:
            return None

        return CommentForModeration(
            comment_id=comment.id,
            group_name=comment.post.group_name,
            post_text=comment.post.text,
            comment_text=comment.text,
            link=comment.post.link,
        )

    async def create_label(
        self,
        data: CreateModerationLabel,
    ) -> None:
        label = CommentModerationLabel(
            comment_id=data.comment_id,
            label=data.label,
        )

        await self.repository.create_label(label)
