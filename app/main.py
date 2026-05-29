from __future__ import annotations

from typing import Dict

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1 import auth, mentor, messages, notifications, projects, tasks, users
from app.core.dependencies import get_db

app = FastAPI(
    title="TeamUp API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# NOTE: allow_credentials=True is incompatible with allow_origins=["*"].
#       In production replace the wildcard with your actual frontend origin(s).
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router,          prefix="/api/v1/auth",          tags=["Authentication"])
app.include_router(users.router,         prefix="/api/v1/users",         tags=["Users"])
app.include_router(projects.router,      prefix="/api/v1/projects",      tags=["Projects"])
app.include_router(tasks.router,         prefix="/api/v1/tasks",         tags=["Tasks"])
app.include_router(messages.router,      prefix="/api/v1/messages",      tags=["Messages"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(mentor.router,        prefix="/api/v1/mentor",        tags=["Mentor"])


# ---------------------------------------------------------------------------
# Core routes
# ---------------------------------------------------------------------------


@app.get("/", tags=["Health"])
async def root() -> Dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, str]:
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exc:  # noqa: BLE001
        return {"status": "ok", "database": "disconnected", "error": str(exc)}
