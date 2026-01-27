"""
API Router Configuration

Combines all API routes into a single router.
"""

from fastapi import APIRouter

from app.api.health import router as health_router

router = APIRouter()

# Include route modules
router.include_router(health_router, prefix="/health", tags=["health"])

# Future routes will be added here:
# router.include_router(auth_router, prefix="/auth", tags=["auth"])
# router.include_router(portfolios_router, prefix="/portfolios", tags=["portfolios"])
# router.include_router(pies_router, prefix="/pies", tags=["pies"])
# router.include_router(slices_router, prefix="/slices", tags=["slices"])
# router.include_router(deposits_router, prefix="/deposits", tags=["deposits"])
# router.include_router(transactions_router, prefix="/transactions", tags=["transactions"])
