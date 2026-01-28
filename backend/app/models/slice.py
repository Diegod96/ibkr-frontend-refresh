"""
Slice Model

Represents an individual holding within a pie.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import Column, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.orm import relationship

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.pie import Pie


class Slice(Base):
    """Slice model - represents an individual holding within a pie."""

    __tablename__ = "slices"
    __table_args__ = (
        UniqueConstraint("pie_id", "symbol", name="uq_slice_pie_symbol"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pie_id = Column(String(36), ForeignKey("pies.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), nullable=False)
    name = Column(String(100), nullable=True)
    target_weight = Column(Numeric(5, 2), nullable=False)
    display_order = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    pie = relationship("Pie", back_populates="slices")

    def __repr__(self) -> str:
        return f"<Slice(id={self.id}, symbol='{self.symbol}', weight={self.target_weight}%)>"
