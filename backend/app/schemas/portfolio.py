"""
Portfolio Schemas

Pydantic schemas for portfolio CRUD operations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PortfolioBase(BaseModel):
    """Base portfolio schema."""

    name: str = Field(..., max_length=100, description="Portfolio name")
    description: Optional[str] = Field(None, description="Portfolio description")
    account_type: Optional[str] = Field(None, description="Account type (roth_ira, traditional_ira, brokerage, etc.)")
    ibkr_account_id: Optional[str] = Field(None, max_length=50, description="IBKR account identifier")
    auto_invest_enabled: bool = Field(default=False, description="Whether auto-invest is enabled")


class PortfolioCreate(PortfolioBase):
    """Schema for creating a portfolio."""
    pass


class PortfolioUpdate(BaseModel):
    """Schema for updating a portfolio."""

    name: Optional[str] = Field(None, max_length=100, description="Portfolio name")
    description: Optional[str] = Field(None, description="Portfolio description")
    account_type: Optional[str] = Field(None, description="Account type")
    ibkr_account_id: Optional[str] = Field(None, max_length=50, description="IBKR account identifier")
    auto_invest_enabled: Optional[bool] = Field(None, description="Whether auto-invest is enabled")


class PortfolioResponse(PortfolioBase):
    """Schema for portfolio response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Portfolio ID")
    user_id: str = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    pie_count: int = Field(default=0, description="Number of pies in this portfolio")
    total_allocation: Decimal = Field(default=Decimal("0"), description="Total allocation across all pies")


class PortfolioListResponse(BaseModel):
    """Schema for portfolio list response."""

    portfolios: list[PortfolioResponse] = Field(..., description="List of portfolios")
    total: int = Field(..., description="Total number of portfolios")
