"""
Slice Service

CRUD operations for Slice management.
"""

from decimal import Decimal
from typing import Any, cast

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pie import Pie
from app.models.slice import Slice


class SliceService:
    """Service class for Slice CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _verify_pie_ownership(self, pie_id: str, portfolio_id: str) -> bool:
        """Verify that a pie belongs to the portfolio."""
        # IDs are expected to be strings
        query = select(Pie.id).where(Pie.id == pie_id, Pie.portfolio_id == portfolio_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_by_id(self, slice_id: str, portfolio_id: str) -> Slice | None:
        """Get a slice by ID, ensuring it belongs to a pie owned by the portfolio."""
        # IDs are expected to be strings

        query = (
            select(Slice).join(Pie).where(Slice.id == slice_id, Pie.portfolio_id == portfolio_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_pie(
        self, pie_id: str, portfolio_id: str, include_inactive: bool = False
    ) -> list[Slice]:
        """Get all slices for a pie."""
        # First verify pie ownership
        if not await self._verify_pie_ownership(pie_id, portfolio_id):
            return []

        # pie_id should be a string

        query = (
            select(Slice)
            .where(Slice.pie_id == pie_id)
            .order_by(Slice.display_order, Slice.created_at)
        )

        if not include_inactive:
            query = query.where(Slice.is_active)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_total_weight(self, pie_id: str) -> Decimal:
        """Get total weight of all active slices in a pie."""
        # pie_id expected to be string

        query = select(Slice.target_weight).where(Slice.pie_id == pie_id, Slice.is_active)
        result = await self.db.execute(query)
        weights = result.scalars().all()
        return sum(weights, Decimal("0"))

    async def create(
        self,
        pie_id: str,
        portfolio_id: str,
        symbol: str,
        target_weight: Decimal,
        name: str | None = None,
        notes: str | None = None,
    ) -> Slice | None:
        """Create a new slice."""
        # Verify pie ownership
        if not await self._verify_pie_ownership(pie_id, portfolio_id):
            return None

        # Check if total weight would exceed 100%
        current_total = await self.get_total_weight(pie_id)
        if current_total + target_weight > Decimal("100"):
            raise ValueError(
                f"Total weight would exceed 100%. Current: {current_total}%, "
                f"New: {target_weight}%, Total would be: {current_total + target_weight}%"
            )

        # Get the next display order
        # pie_id expected to be string

        max_order_query = (
            select(Slice.display_order)
            .where(Slice.pie_id == pie_id)
            .order_by(Slice.display_order.desc())
            .limit(1)
        )
        result = await self.db.execute(max_order_query)
        max_order = result.scalar_one_or_none() or 0

        slice_obj = Slice(
            pie_id=pie_id,
            symbol=symbol.upper(),
            name=name,
            target_weight=target_weight,
            notes=notes,
            display_order=max_order + 1,
        )
        self.db.add(slice_obj)
        await self.db.flush()
        await self.db.refresh(slice_obj)
        return slice_obj

    async def update(
        self,
        slice_id: str,
        portfolio_id: str,
        symbol: str | None = None,
        name: str | None = None,
        target_weight: Decimal | None = None,
        notes: str | None = None,
        is_active: bool | None = None,
    ) -> Slice | None:
        """Update a slice."""
        slice_obj = await self.get_by_id(slice_id, portfolio_id)
        if not slice_obj:
            return None

        # If updating weight, check total doesn't exceed 100%
        # Cast the ORM instance to Any so mypy doesn't treat attributes as Column[...] types
        s = cast(Any, slice_obj)

        if target_weight is not None and target_weight != s.target_weight:
            current_total = await self.get_total_weight(cast(str, s.pie_id))
            new_total = current_total - s.target_weight + target_weight
            if new_total > Decimal("100"):
                raise ValueError(
                    f"Total weight would exceed 100%. New total would be: {new_total}%"
                )

        if symbol is not None:
            s.symbol = symbol.upper()
        if name is not None:
            s.name = name
        if target_weight is not None:
            s.target_weight = target_weight
        if notes is not None:
            s.notes = notes
        if is_active is not None:
            s.is_active = is_active

        await self.db.flush()
        await self.db.refresh(slice_obj)
        return slice_obj

    async def delete(self, slice_id: str, portfolio_id: str) -> bool:
        """Delete a slice."""
        slice_obj = await self.get_by_id(slice_id, portfolio_id)
        if not slice_obj:
            return False

        query = delete(Slice).where(Slice.id == slice_id)
        result = await self.db.execute(query)
        # SQLAlchemy Result typing may not expose rowcount; cast to Any for runtime access
        return cast(Any, result).rowcount > 0

    async def reorder(self, pie_id: str, portfolio_id: str, slice_ids: list[str]) -> bool:
        """Reorder slices by updating their display_order."""
        # Verify pie ownership
        if not await self._verify_pie_ownership(pie_id, portfolio_id):
            return False
        # pie_id expected to be string

        for index, slice_id in enumerate(slice_ids):
            # slice_id expected to be a string

            query = (
                update(Slice)
                .where(Slice.id == slice_id, Slice.pie_id == pie_id)
                .values(display_order=index)
            )
            await self.db.execute(query)
        return True
