"""
Portfolio Model
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from .user import User
    from .pie import Pie


class Portfolio(Base):
    """Portfolio model representing user investment accounts."""

    __tablename__ = "portfolios"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    account_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ibkr_account_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    auto_invest_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="portfolios")
    pies: Mapped[list["Pie"]] = relationship("Pie", back_populates="portfolio", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Portfolio(id={self.id}, name={self.name}, user_id={self.user_id})>"