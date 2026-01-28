"""
Pie Service

CRUD operations for Pie management.
"""

from decimal import Decimal
from typing import Any, cast

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.pie import Pie


class PieService:
    """Service class for Pie CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, pie_id: str, portfolio_id: str) -> Pie | None:
        """Get a pie by ID, ensuring it belongs to the portfolio."""
        # IDs are expected to be strings

        query = (
            select(Pie)
            .options(selectinload(Pie.slices))
            .where(Pie.id == pie_id, Pie.portfolio_id == portfolio_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_portfolio(
        self, portfolio_id: str, include_inactive: bool = False
    ) -> list[Pie]:
        """Get all pies for a portfolio."""
        # portfolio_id should be a string

        query = (
            select(Pie)
            .options(selectinload(Pie.slices))
            .where(Pie.portfolio_id == portfolio_id)
            .order_by(Pie.display_order, Pie.created_at)
        )

        if not include_inactive:
            query = query.where(Pie.is_active)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(
        self,
        portfolio_id: str,
        name: str,
        description: str | None = None,
        color: str = "#3B82F6",
        icon: str | None = None,
        target_allocation: Decimal = Decimal("0"),
    ) -> Pie:
        """Create a new pie."""
        # Get the next display order (portfolio_id is expected to be a string)

        max_order_query = (
            select(Pie.display_order)
            .where(Pie.portfolio_id == portfolio_id)
            .order_by(Pie.display_order.desc())
            .limit(1)
        )
        result = await self.db.execute(max_order_query)
        max_order = result.scalar_one_or_none() or 0

        pie = Pie(
            portfolio_id=portfolio_id,
            name=name,
            description=description,
            color=color,
            icon=icon,
            target_allocation=target_allocation,
            display_order=max_order + 1,
        )
        self.db.add(pie)
        await self.db.flush()
        # Ensure slices relationship is available without triggering lazy load later
        await self.db.refresh(pie, ["slices"])
        return pie

    async def update(
        self,
        pie_id: str,
        portfolio_id: str,
        name: str | None = None,
        description: str | None = None,
        color: str | None = None,
        icon: str | None = None,
        target_allocation: Decimal | None = None,
        is_active: bool | None = None,
    ) -> Pie | None:
        """Update a pie."""
        pie = await self.get_by_id(pie_id, portfolio_id)
        if not pie:
            return None

        p = cast(Any, pie)

        if name is not None:
            p.name = name
        if description is not None:
            p.description = description
        if color is not None:
            p.color = color
        if icon is not None:
            p.icon = icon
        if target_allocation is not None:
            p.target_allocation = target_allocation
        if is_active is not None:
            p.is_active = is_active

        await self.db.flush()
        await self.db.refresh(pie)
        return pie

    async def delete(self, pie_id: str, portfolio_id: str) -> bool:
        """Delete a pie (and all its slices via cascade)."""
        # IDs expected as strings
        query = delete(Pie).where(Pie.id == pie_id, Pie.portfolio_id == portfolio_id)
        result = await self.db.execute(query)
        return cast(Any, result).rowcount > 0

    async def reorder(self, portfolio_id: str, pie_ids: list[str]) -> bool:
        """Reorder pies by updating their display_order."""
        # portfolio_id and pie_ids are expected to be strings

        for index, pie_id in enumerate(pie_ids):
            query = (
                update(Pie)
                .where(Pie.id == pie_id, Pie.portfolio_id == portfolio_id)
                .values(display_order=index)
            )
            await self.db.execute(query)
        return True

    async def get_total_allocation(self, portfolio_id: str) -> Decimal:
        """Get total allocation percentage across all active pies."""
        pies = await self.get_all_by_portfolio(portfolio_id)
        from decimal import Decimal

        # cast pie instances to Any to avoid mypy treating attributes as Column types
        return sum((cast(Any, pie).target_allocation for pie in pies), Decimal("0"))
