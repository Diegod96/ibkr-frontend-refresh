"""
Portfolio Service

Business logic for portfolio operations.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Portfolio
from app.models.user import User
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate
from app.services.base import BaseService


class PortfolioService(BaseService[Portfolio]):
    """Service for portfolio operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Portfolio)

    async def get_user_portfolios(self, user_id: str) -> List[Portfolio]:
        """Get all portfolios for a user."""
        query = select(Portfolio).where(Portfolio.user_id == user_id).order_by(Portfolio.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_portfolio(self, user_id: str, portfolio_data: PortfolioCreate) -> Portfolio:
        """Create a new portfolio for a user."""
        portfolio_dict = portfolio_data.model_dump()
        portfolio_dict["user_id"] = user_id

        portfolio = Portfolio(**portfolio_dict)
        self.session.add(portfolio)
        await self.session.commit()
        await self.session.refresh(portfolio)
        return portfolio

    async def update_portfolio(self, portfolio_id: str, updates: PortfolioUpdate) -> Optional[Portfolio]:
        """Update a portfolio."""
        portfolio = await self.get_by_id(portfolio_id)
        if not portfolio:
            return None

        update_data = updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(portfolio, field, value)

        await self.session.commit()
        await self.session.refresh(portfolio)
        return portfolio

    async def delete_portfolio(self, portfolio_id: str) -> bool:
        """Delete a portfolio."""
        portfolio = await self.get_by_id(portfolio_id)
        if not portfolio:
            return False

        await self.session.delete(portfolio)
        await self.session.commit()
        return True

    async def get_portfolio_with_details(self, portfolio_id: str) -> Optional[Portfolio]:
        """Get a portfolio with its pies and slices loaded."""
        query = select(Portfolio).where(Portfolio.id == portfolio_id)
        result = await self.session.execute(query)
        portfolio = result.scalar_one_or_none()

        if portfolio:
            # Load pies and their slices
            await self.session.refresh(portfolio, ["pies"])
            for pie in portfolio.pies:
                await self.session.refresh(pie, ["slices"])

        return portfolio
