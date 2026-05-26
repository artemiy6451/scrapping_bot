from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.scaffolding_backend.repositories.comments import CommentRepository
from app.scaffolding_backend.schemas.comment import CommentForModeration
from app.scaffolding_backend.schemas.moderation import CreateModerationLabel
from app.scaffolding_backend.services.moderation_service import ModerationService

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/next")
async def get_next_comment(
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> CommentForModeration:
    repository = CommentRepository(session)

    service = ModerationService(repository)

    comment = await service.get_next_comment()

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="No unlabeled comments",
        )

    return comment


@router.post("/label")
async def label_comment(
    data: CreateModerationLabel,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> dict:
    repository = CommentRepository(session)

    service = ModerationService(repository)

    await service.create_label(data)

    return {
        "status": "ok",
    }
