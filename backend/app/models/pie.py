"""
Pie Model

Represents a themed portfolio group containing slices.
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, text
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    pass


class Pie(Base):
    """Pie model - represents a themed portfolio group."""

    __tablename__ = "pies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(
        String(36), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#3B82F6")
    icon = Column(String(50), nullable=True)
    target_allocation = Column(Numeric(5, 2), default=Decimal("0"))
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    portfolio = relationship("Portfolio", back_populates="pies")
    slices = relationship(
        "Slice", back_populates="pie", cascade="all, delete-orphan", order_by="Slice.display_order"
    )

    def __repr__(self) -> str:
        return f"<Pie(id={self.id}, name='{self.name}')>"

    @property
    def total_slice_weight(self) -> Decimal:
        """Calculate total weight of all active slices."""
        return (
            sum(slice.target_weight for slice in self.slices if slice.is_active)
            if self.slices
            else Decimal("0")
        )

    @property
    def slice_count(self) -> int:
        """Count of active slices."""
        return len([s for s in self.slices if s.is_active]) if self.slices else 0
