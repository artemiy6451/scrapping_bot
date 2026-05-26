import csv
from io import StringIO

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_session
from app.scaffolding_backend.models.moderation_label import (
    CommentModerationLabel,
)

router = APIRouter(prefix="/dataset", tags=["dataset"])


@router.get("/export")
async def export_dataset(
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> StreamingResponse:
    stmt = select(CommentModerationLabel).options(
        joinedload(CommentModerationLabel.comment).joinedload("post")  # type: ignore
    )

    result = await session.execute(stmt)

    labels = result.scalars().all()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow(
        [
            "post_text",
            "comment_text",
            "label",
        ]
    )

    for item in labels:
        writer.writerow(
            [
                item.comment.post.text,
                item.comment.text,
                item.label,
            ]
        )

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": ("attachment; filename=dataset.csv")},
    )
