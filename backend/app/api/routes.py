"""
API Router Configuration

Combines all API routes into a single router.
"""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.ibkr import router as ibkr_router
from app.api.pies import router as pies_router
from app.api.portfolios import router as portfolios_router
from app.api.rebalance import router as rebalance_router
from app.api.slices import router as slices_router

router = APIRouter()

# Include route modules
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(ibkr_router, prefix="/ibkr", tags=["ibkr"])
router.include_router(portfolios_router, prefix="/portfolios", tags=["portfolios"])
router.include_router(rebalance_router, prefix="/rebalance", tags=["rebalance"])
router.include_router(pies_router)
router.include_router(slices_router)

# Future routes will be added here:
# router.include_router(deposits_router, prefix="/deposits", tags=["deposits"])
# router.include_router(transactions_router, prefix="/transactions", tags=["transactions"])
