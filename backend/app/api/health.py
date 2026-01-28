"""
Health Check Endpoint

Provides endpoints for monitoring application health.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

router = APIRouter()


@router.get("")
async def health_check() -> dict[str, Any]:
    """
    Basic health check endpoint.

    Returns application status and version information.
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """
    Readiness check endpoint.

    Verifies database connectivity and returns detailed status.
    """
    db_status = "healthy"
    db_message = "Connected"

    try:
        # Test database connection
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "unhealthy"
        db_message = str(e)

    return {
        "status": "ready" if db_status == "healthy" else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": {
                "status": db_status,
                "message": db_message,
            }
        },
    }


@router.get("/live")
async def liveness_check() -> dict[str, str]:
    """
    Liveness check endpoint.

    Simple check to verify the application is running.
    Used by orchestrators like Kubernetes for health monitoring.
    """
    return {"status": "alive"}
