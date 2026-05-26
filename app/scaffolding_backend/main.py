from fastapi import FastAPI

import app.scaffolding_backend.models  # noqa: F401
from app.scaffolding_backend.api.comments import router as comments_router
from app.scaffolding_backend.api.dataset import router as dataset_router

fastapi = FastAPI(
    title="Moderation Platform",
)

fastapi.include_router(comments_router)
fastapi.include_router(dataset_router)
