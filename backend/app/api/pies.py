"""
Pie API Endpoints

CRUD endpoints for managing pies.
"""

from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUserId, get_db
from app.schemas.pie_slice import (
    PieCreate,
    PieUpdate,
    PieWithSlicesResponse,
    PieListResponse,
    ReorderRequest,
)
from app.schemas.portfolio import PortfolioCreate
from app.services.pie_service import PieService
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/pies", tags=["pies"])


async def _get_user_default_portfolio(user_id: str, db: AsyncSession) -> str:
    """Get or create a default portfolio for the user."""
    portfolio_service = PortfolioService(db)
    portfolios = await portfolio_service.get_user_portfolios(str(user_id))
    
    # Return existing default portfolio if it exists
    for portfolio in portfolios:
        if portfolio.name == "Default Portfolio":
            return str(portfolio.id)
    
    # Create default portfolio if none exists
    default_portfolio = await portfolio_service.create_portfolio(
        str(user_id),
        PortfolioCreate(name="Default Portfolio", description="Default portfolio for pies")
    )
    return str(default_portfolio.id)


def _pie_to_response(pie, user_id: Optional[str] = None) -> PieWithSlicesResponse:
    """Convert a Pie model to response schema."""
    # Ensure user_id is a string for the response schema
    # user_id is expected to already be a string

    return PieWithSlicesResponse(
        id=pie.id,
        portfolio_id=pie.portfolio_id,
        user_id=user_id or None,
        name=pie.name,
        description=pie.description,
        color=pie.color,
        icon=pie.icon,
        target_allocation=pie.target_allocation,
        display_order=pie.display_order,
        is_active=pie.is_active,
        created_at=pie.created_at,
        updated_at=pie.updated_at,
        slices=[
            {
                "id": s.id,
                "pie_id": s.pie_id,
                "symbol": s.symbol,
                "name": s.name,
                "target_weight": s.target_weight,
                "display_order": s.display_order,
                "notes": s.notes,
                "is_active": s.is_active,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
            }
            for s in (pie.slices or [])
            if s.is_active
        ],
        total_slice_weight=pie.total_slice_weight,
        slice_count=pie.slice_count,
    )


@router.get("", response_model=PieListResponse)
async def get_pies(
    user_id: CurrentUserId,
    include_inactive: bool = False,
    portfolio_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all pies for the current user."""
    service = PieService(db)
    # If portfolio_id provided in query, validate ownership
    if portfolio_id is not None:
        portfolio_service = PortfolioService(db)
        user_portfolios = await portfolio_service.get_user_portfolios(str(user_id))
        if not any(p.id == portfolio_id for p in user_portfolios):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Portfolio does not belong to the user",
            )
        selected_portfolio = portfolio_id
    else:
        selected_portfolio = await _get_user_default_portfolio(user_id, db)

    pies = await service.get_all_by_portfolio(selected_portfolio, include_inactive=include_inactive)
    total_allocation = await service.get_total_allocation(selected_portfolio)
    
    return PieListResponse(
        pies=[_pie_to_response(p, user_id=user_id) for p in pies],
        total_allocation=total_allocation,
    )


@router.get("/{pie_id}", response_model=PieWithSlicesResponse)
async def get_pie(
    pie_id: str,
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific pie by ID."""
    service = PieService(db)
    portfolio_id = await _get_user_default_portfolio(user_id, db)
    pie = await service.get_by_id(pie_id, portfolio_id)
    
    if not pie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pie not found",
        )
    
    return _pie_to_response(pie, user_id=user_id)


@router.post("", response_model=PieWithSlicesResponse, status_code=status.HTTP_201_CREATED)
async def create_pie(
    data: PieCreate,
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
):
    """Create a new pie."""
    service = PieService(db)
    # Determine portfolio: use provided portfolio_id or user's default
    if data.portfolio_id:
        # validate the portfolio belongs to the user
        portfolio_service = PortfolioService(db)
        user_portfolios = await portfolio_service.get_user_portfolios(str(user_id))
        if not any(p.id == data.portfolio_id for p in user_portfolios):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Portfolio does not belong to the user",
            )
        portfolio_id = data.portfolio_id
    else:
        portfolio_id = await _get_user_default_portfolio(user_id, db)

    # Check total allocation won't exceed 100%
    current_total = await service.get_total_allocation(portfolio_id)
    if current_total + data.target_allocation > Decimal("100"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Total allocation would exceed 100%. Current: {current_total}%, "
                    f"Requested: {data.target_allocation}%",
        )
    
    pie = await service.create(
        portfolio_id=portfolio_id,
        name=data.name,
        description=data.description,
        color=data.color,
        icon=data.icon,
        target_allocation=data.target_allocation,
    )
    
    return _pie_to_response(pie, user_id=user_id)


@router.patch("/{pie_id}", response_model=PieWithSlicesResponse)
async def update_pie(
    pie_id: str,
    data: PieUpdate,
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
):
    """Update a pie."""
    service = PieService(db)
    # Determine portfolio: allow overriding via payload
    if getattr(data, "portfolio_id", None):
        portfolio_service = PortfolioService(db)
        user_portfolios = await portfolio_service.get_user_portfolios(str(user_id))
        if not any(p.id == data.portfolio_id for p in user_portfolios):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Portfolio does not belong to the user",
            )
        portfolio_id = data.portfolio_id
    else:
        portfolio_id = await _get_user_default_portfolio(user_id, db)

    # If updating allocation, check it won't exceed 100%
    if data.target_allocation is not None:
        existing_pie = await service.get_by_id(pie_id, portfolio_id)
        if not existing_pie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pie not found",
            )
        
        current_total = await service.get_total_allocation(portfolio_id)
        new_total = current_total - existing_pie.target_allocation + data.target_allocation
        if new_total > Decimal("100"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Total allocation would exceed 100%. New total would be: {new_total}%",
            )
    
    pie = await service.update(
        pie_id=pie_id,
        portfolio_id=portfolio_id,
        name=data.name,
        description=data.description,
        color=data.color,
        icon=data.icon,
        target_allocation=data.target_allocation,
        is_active=data.is_active,
    )
    
    if not pie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pie not found",
        )
    
    return _pie_to_response(pie)


@router.delete("/{pie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pie(
    pie_id: str,
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
):
    """Delete a pie and all its slices."""
    service = PieService(db)
    portfolio_id = await _get_user_default_portfolio(user_id, db)
    deleted = await service.delete(pie_id, portfolio_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pie not found",
        )


@router.post("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_pies(
    data: ReorderRequest,
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
):
    """Reorder pies by providing a list of pie IDs in the desired order."""
    service = PieService(db)
    portfolio_id = await _get_user_default_portfolio(user_id, db)
    await service.reorder(portfolio_id, data.ids)
