"""
Pie and Slice Schemas

Pydantic schemas for Pie and Slice API endpoints.
"""

from datetime import datetime
from decimal import Decimal

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
    name: str | None = Field(None, max_length=100, description="Company name")
    target_weight: Decimal = Field(..., gt=0, le=100, description="Target weight percentage")
    notes: str | None = Field(None, description="Optional notes")

    @field_validator("symbol")
    @classmethod
    def uppercase_symbol(cls, v: str) -> str:
        return v.upper().strip()


class SliceCreate(SliceBase):
    """Schema for creating a slice."""

    pass


class SliceUpdate(BaseSchema):
    """Schema for updating a slice."""

    symbol: str | None = Field(None, min_length=1, max_length=20)
    name: str | None = Field(None, max_length=100)
    target_weight: Decimal | None = Field(None, gt=0, le=100)
    notes: str | None = None
    is_active: bool | None = None

    @field_validator("symbol")
    @classmethod
    def uppercase_symbol(cls, v: str | None) -> str | None:
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
    description: str | None = Field(None, description="Pie description")
    color: str = Field("#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code")
    icon: str | None = Field(None, max_length=50, description="Icon identifier")
    target_allocation: Decimal = Field(
        Decimal("0"), ge=0, le=100, description="Target allocation percentage"
    )


class PieCreate(PieBase):
    """Schema for creating a pie."""

    # Optional portfolio_id: if provided, pie will be created in that portfolio
    portfolio_id: str | None = None


class PieUpdate(BaseSchema):
    """Schema for updating a pie."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: str | None = Field(None, max_length=50)
    target_allocation: Decimal | None = Field(None, ge=0, le=100)
    is_active: bool | None = None
    portfolio_id: str | None = None


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

    slices: list[SliceResponse] = []
    total_slice_weight: Decimal = Decimal("0")
    slice_count: int = 0


# ============================================================================
# List Response Schemas
# ============================================================================


class PieListResponse(BaseSchema):
    """Schema for list of pies response."""

    pies: list[PieWithSlicesResponse]
    total_allocation: Decimal = Decimal("0")


# ============================================================================
# Reorder Schemas
# ============================================================================


class ReorderRequest(BaseSchema):
    """Schema for reordering items."""

    ids: list[str] = Field(..., min_length=1, description="Ordered list of IDs")
