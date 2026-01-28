"""
Portfolio API Routes

CRUD operations for portfolios.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUserId, get_db
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioListResponse,
    PortfolioResponse,
    PortfolioUpdate,
)
from app.services.portfolio_service import PortfolioService

router = APIRouter()


@router.get("/", response_model=PortfolioListResponse)
async def get_portfolios(
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
) -> PortfolioListResponse:
    """Get all portfolios for the current user."""
    service = PortfolioService(db)
    portfolios = await service.get_user_portfolios(user_id)

    # Convert to response models with additional data
    portfolio_responses = []
    for portfolio in portfolios:
        pie_count = len(portfolio.pies) if portfolio.pies else 0
        total_allocation = sum(
            pie.target_allocation for pie in (portfolio.pies or []) if pie.is_active
        )

        portfolio_dict = portfolio.__dict__.copy()
        portfolio_dict["pie_count"] = pie_count
        portfolio_dict["total_allocation"] = total_allocation

        portfolio_responses.append(PortfolioResponse(**portfolio_dict))

    return PortfolioListResponse(
        portfolios=portfolio_responses,
        total=len(portfolio_responses)
    )


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
) -> PortfolioResponse:
    """Create a new portfolio."""
    service = PortfolioService(db)

    # Check for duplicate portfolio name
    existing_portfolios = await service.get_user_portfolios(user_id)
    if any(p.name.lower() == portfolio_data.name.lower() for p in existing_portfolios):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Portfolio with name '{portfolio_data.name}' already exists"
        )

    portfolio = await service.create_portfolio(user_id, portfolio_data)

    return PortfolioResponse(
        **portfolio.__dict__,
        pie_count=0,
        total_allocation=0
    )


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: UUID,
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
) -> PortfolioResponse:
    """Get a specific portfolio by ID."""
    service = PortfolioService(db)
    portfolio = await service.get_portfolio_with_details(portfolio_id)

    if not portfolio or portfolio.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )

    pie_count = len(portfolio.pies) if portfolio.pies else 0
    total_allocation = sum(
        pie.target_allocation for pie in (portfolio.pies or []) if pie.is_active
    )

    return PortfolioResponse(
        **portfolio.__dict__,
        pie_count=pie_count,
        total_allocation=total_allocation
    )


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: UUID,
    portfolio_data: PortfolioUpdate,
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
) -> PortfolioResponse:
    """Update a portfolio."""
    service = PortfolioService(db)

    # Get current portfolio
    portfolio = await service.get_portfolio_with_details(portfolio_id)
    if not portfolio or portfolio.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )

    # Check for duplicate name if name is being updated
    if portfolio_data.name is not None and portfolio_data.name != portfolio.name:
        existing_portfolios = await service.get_user_portfolios(user_id)
        if any(p.name.lower() == portfolio_data.name.lower() and p.id != portfolio_id for p in existing_portfolios):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Portfolio with name '{portfolio_data.name}' already exists"
            )

    updated_portfolio = await service.update_portfolio(portfolio_id, portfolio_data)
    if not updated_portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )

    pie_count = len(updated_portfolio.pies) if updated_portfolio.pies else 0
    total_allocation = sum(
        pie.target_allocation for pie in (updated_portfolio.pies or []) if pie.is_active
    )

    return PortfolioResponse(
        **updated_portfolio.__dict__,
        pie_count=pie_count,
        total_allocation=total_allocation
    )


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: UUID,
    user_id: CurrentUserId,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a portfolio."""
    service = PortfolioService(db)

    # Verify ownership
    portfolio = await service.get_by_id(portfolio_id)
    if not portfolio or portfolio.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )

    # Check if portfolio has pies
    if portfolio.pies and len(portfolio.pies) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete portfolio with existing pies. Please delete all pies first."
        )

    success = await service.delete_portfolio(portfolio_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )