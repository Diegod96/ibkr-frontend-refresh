"""
Pie and Slice Schemas

Pydantic schemas for Pie and Slice API endpoints.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# Base Schemas
# ============================================================================

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ============================================================================
# Slice Schemas
# ============================================================================

class SliceBase(BaseSchema):
    """Base slice schema."""
    symbol: str = Field(..., min_length=1, max_length=20, description="Stock ticker symbol")
    name: Optional[str] = Field(None, max_length=100, description="Company name")
    target_weight: Decimal = Field(..., gt=0, le=100, description="Target weight percentage")
    notes: Optional[str] = Field(None, description="Optional notes")

    @field_validator('symbol')
    @classmethod
    def uppercase_symbol(cls, v: str) -> str:
        return v.upper().strip()


class SliceCreate(SliceBase):
    """Schema for creating a slice."""
    pass


class SliceUpdate(BaseSchema):
    """Schema for updating a slice."""
    symbol: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, max_length=100)
    target_weight: Optional[Decimal] = Field(None, gt=0, le=100)
    notes: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator('symbol')
    @classmethod
    def uppercase_symbol(cls, v: Optional[str]) -> Optional[str]:
        return v.upper().strip() if v else v


class SliceResponse(SliceBase):
    """Schema for slice response."""
    id: str
    pie_id: str
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Pie Schemas
# ============================================================================

class PieBase(BaseSchema):
    """Base pie schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Pie name")
    description: Optional[str] = Field(None, description="Pie description")
    color: str = Field("#3B82F6", pattern=r'^#[0-9A-Fa-f]{6}$', description="Hex color code")
    icon: Optional[str] = Field(None, max_length=50, description="Icon identifier")
    target_allocation: Decimal = Field(Decimal("0"), ge=0, le=100, description="Target allocation percentage")


class PieCreate(PieBase):
    """Schema for creating a pie."""
    # Optional portfolio_id: if provided, pie will be created in that portfolio
    portfolio_id: Optional[str] = None


class PieUpdate(BaseSchema):
    """Schema for updating a pie."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)
    target_allocation: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None
    portfolio_id: Optional[str] = None


class PieResponse(PieBase):
    """Schema for pie response (without slices)."""
    id: str
    portfolio_id: str
    user_id: str
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PieWithSlicesResponse(PieResponse):
    """Schema for pie response with slices included."""
    slices: List[SliceResponse] = []
    total_slice_weight: Decimal = Decimal("0")
    slice_count: int = 0


# ============================================================================
# List Response Schemas
# ============================================================================

class PieListResponse(BaseSchema):
    """Schema for list of pies response."""
    pies: List[PieWithSlicesResponse]
    total_allocation: Decimal = Decimal("0")


# ============================================================================
# Reorder Schemas
# ============================================================================

class ReorderRequest(BaseSchema):
    """Schema for reordering items."""
    ids: List[str] = Field(..., min_length=1, description="Ordered list of IDs")
