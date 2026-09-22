from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api import (
    auth,
    chats,
    media,
    messages,
    search,
    settings as settings_api,
    users,
    websocket,
)
from backend.config import settings
from backend.core.telegram import telegram_manager


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


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
app.include_router(websocket.router)


# Serve frontend static files.
app.mount(
    "/frontend",
    StaticFiles(directory=FRONTEND_DIR),
    name="frontend",
)


@app.get("/")
async def root():
    """Serve the Telefarm web application."""

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


@app.get("/health")
async def health() -> dict:
    """Return application health status."""

    return {
        "status": "healthy",
        "service": "Telefarm",
    }
