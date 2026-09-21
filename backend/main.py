from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import (
    auth,
    chats,
    media,
    messages,
    search,
    settings as settings_api,
    users,
)
from backend.config import settings
from backend.core.telegram import telegram_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    yield

    await telegram_manager.disconnect_all()


app = FastAPI(
    title="Telefarm",
    description="Telefarm Telegram web client backend.",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(chats.router)
app.include_router(messages.router)
app.include_router(media.router)
app.include_router(users.router)
app.include_router(search.router)
app.include_router(settings_api.router)


@app.get("/")
async def root() -> dict:
    """Return basic application information."""
    return {
        "name": "Telefarm",
        "status": "online",
        "version": "1.0.0",
    }


@app.get("/health")
async def health() -> dict:
    """Return the application health status."""
    return {
        "status": "healthy",
        "service": "Telefarm",
    }
