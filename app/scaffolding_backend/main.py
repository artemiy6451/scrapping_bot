from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.scaffolding_backend.models  # noqa: F401
from app.scaffolding_backend.api.comments import router as comments_router
from app.scaffolding_backend.api.dataset import router as dataset_router

fastapi = FastAPI(
    title="Moderation Platform",
)

fastapi.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi.include_router(comments_router)
fastapi.include_router(dataset_router)
