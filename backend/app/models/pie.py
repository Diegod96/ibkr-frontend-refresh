"""
Pie Model

Represents a themed portfolio group containing slices.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.portfolio import Portfolio
    from app.models.slice import Slice


class Pie(Base):
    """Pie model - represents a themed portfolio group."""

    __tablename__ = "pies"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default="gen_random_uuid()")
    portfolio_id: Mapped[UUID] = mapped_column(ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(7), default="#3B82F6")
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_allocation: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="pies")
    slices: Mapped[List["Slice"]] = relationship(
        "Slice",
        back_populates="pie",
        cascade="all, delete-orphan",
        order_by="Slice.display_order"
    )

    def __repr__(self) -> str:
        return f"<Pie(id={self.id}, name='{self.name}', user_id={self.user_id})>"

    @property
    def total_slice_weight(self) -> Decimal:
        """Calculate total weight of all active slices."""
        return sum(
            slice.target_weight for slice in self.slices if slice.is_active
        ) if self.slices else Decimal("0")

    @property
    def slice_count(self) -> int:
        """Count of active slices."""
        return len([s for s in self.slices if s.is_active]) if self.slices else 0
