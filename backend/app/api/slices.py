"""
Slice API Endpoints

CRUD endpoints for managing slices within pies.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUserId, get_db
from app.schemas.pie_slice import (
    ReorderRequest,
    SliceCreate,
    SliceResponse,
    SliceUpdate,
)
from app.schemas.portfolio import PortfolioCreate
from app.services.portfolio_service import PortfolioService
from app.services.slice_service import SliceService

router = APIRouter(prefix="/pies/{pie_id}/slices", tags=["slices"])


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
        PortfolioCreate(
            name="Default Portfolio",
            description="Default portfolio for pies",
            account_type=None,
            ibkr_account_id=None,
        ),
    )
    return str(default_portfolio.id)


def _slice_to_response(slice_obj) -> SliceResponse:
    """Convert a Slice model to response schema."""
    return SliceResponse(
        id=slice_obj.id,
        pie_id=slice_obj.pie_id,
        symbol=slice_obj.symbol,
        name=slice_obj.name,
        target_weight=slice_obj.target_weight,
        display_order=slice_obj.display_order,
        notes=slice_obj.notes,
        is_active=slice_obj.is_active,
        created_at=slice_obj.created_at,
        updated_at=slice_obj.updated_at,
    )


@router.get("", response_model=list[SliceResponse])
async def get_slices(
    pie_id: str,
    user_id: CurrentUserId,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Get all slices for a pie."""
    service = SliceService(db)
    portfolio_id = await _get_user_default_portfolio(user_id, db)
    slices = await service.get_all_by_pie(pie_id, portfolio_id, include_inactive=include_inactive)
    return [_slice_to_response(s) for s in slices]


@router.get("/{slice_id}", response_model=SliceResponse)
async def get_slice(
    pie_id: str,
    slice_id: str,
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific slice by ID."""
    service = SliceService(db)
    portfolio_id = await _get_user_default_portfolio(user_id, db)
    slice_obj = await service.get_by_id(slice_id, portfolio_id)

    if not slice_obj or slice_obj.pie_id != pie_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slice not found",
        )

    return _slice_to_response(slice_obj)


@router.post("", response_model=SliceResponse, status_code=status.HTTP_201_CREATED)
async def create_slice(
    pie_id: str,
    data: SliceCreate,
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
):
    """Create a new slice in a pie."""
    service = SliceService(db)
    portfolio_id = await _get_user_default_portfolio(user_id, db)

    try:
        slice_obj = await service.create(
            pie_id=pie_id,
            portfolio_id=portfolio_id,
            symbol=data.symbol,
            target_weight=data.target_weight,
            name=data.name,
            notes=data.notes,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    if not slice_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pie not found",
        )

    return _slice_to_response(slice_obj)


@router.patch("/{slice_id}", response_model=SliceResponse)
async def update_slice(
    pie_id: str,
    slice_id: str,
    data: SliceUpdate,
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
):
    """Update a slice."""
    service = SliceService(db)
    portfolio_id = await _get_user_default_portfolio(user_id, db)

    # Verify the slice belongs to this pie
    existing = await service.get_by_id(slice_id, portfolio_id)
    if not existing or existing.pie_id != pie_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slice not found",
        )

    try:
        slice_obj = await service.update(
            slice_id=slice_id,
            portfolio_id=portfolio_id,
            symbol=data.symbol,
            name=data.name,
            target_weight=data.target_weight,
            notes=data.notes,
            is_active=data.is_active,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    if not slice_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slice not found",
        )

    return _slice_to_response(slice_obj)


@router.delete("/{slice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_slice(
    pie_id: str,
    slice_id: str,
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
):
    """Delete a slice from a pie."""
    service = SliceService(db)
    portfolio_id = await _get_user_default_portfolio(user_id, db)

    # Verify the slice belongs to this pie
    existing = await service.get_by_id(slice_id, portfolio_id)
    if not existing or existing.pie_id != pie_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slice not found",
        )

    deleted = await service.delete(slice_id, portfolio_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slice not found",
        )

    deleted = await service.delete(slice_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slice not found",
        )


@router.post("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_slices(
    pie_id: str,
    data: ReorderRequest,
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
):
    """Reorder slices by providing a list of slice IDs in the desired order."""
    service = SliceService(db)
    portfolio_id = await _get_user_default_portfolio(user_id, db)
    success = await service.reorder(pie_id, portfolio_id, data.ids)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pie not found",
        )
