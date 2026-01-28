"""
Base Schemas

Common schema patterns and base classes.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""

    created_at: datetime
    updated_at: datetime


class UUIDMixin(BaseModel):
    """Mixin for ID primary key stored as string."""

    id: str


# ============================================================================
# User Schemas
# ============================================================================


class UserBase(BaseSchema):
    """Base user schema."""

    email: str
    display_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    pass


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    display_name: Optional[str] = None
    ibkr_connected: Optional[bool] = None


class UserResponse(UserBase, UUIDMixin, TimestampMixin):
    """Schema for user response."""

    ibkr_connected: bool


# ============================================================================
# Portfolio Schemas
# ============================================================================


class PortfolioBase(BaseSchema):
    """Base portfolio schema."""

    name: str
    description: Optional[str] = None
    account_type: Optional[str] = None
    ibkr_account_id: Optional[str] = None
    auto_invest_enabled: bool = False


class PortfolioCreate(PortfolioBase):
    """Schema for creating a portfolio."""

    pass


class PortfolioUpdate(BaseSchema):
    """Schema for updating a portfolio."""

    name: Optional[str] = None
    description: Optional[str] = None
    account_type: Optional[str] = None
    ibkr_account_id: Optional[str] = None
    auto_invest_enabled: Optional[bool] = None


class PortfolioResponse(PortfolioBase, UUIDMixin, TimestampMixin):
    """Schema for portfolio response."""

    user_id: str


# ============================================================================
# Pie Schemas
# ============================================================================


class PieBase(BaseSchema):
    """Base pie schema."""

    name: str
    description: Optional[str] = None
    target_weight: float
    color: Optional[str] = None


class PieCreate(PieBase):
    """Schema for creating a pie."""

    portfolio_id: str


class PieUpdate(BaseSchema):
    """Schema for updating a pie."""

    name: Optional[str] = None
    description: Optional[str] = None
    target_weight: Optional[float] = None
    color: Optional[str] = None


class PieResponse(PieBase, UUIDMixin, TimestampMixin):
    """Schema for pie response."""

    portfolio_id: str


# ============================================================================
# Slice Schemas
# ============================================================================


class SliceBase(BaseSchema):
    """Base slice schema."""

    ticker: str
    name: Optional[str] = None
    target_weight: float
    position_type: str = "full"


class SliceCreate(SliceBase):
    """Schema for creating a slice."""

    pie_id: str


class SliceUpdate(BaseSchema):
    """Schema for updating a slice."""

    name: Optional[str] = None
    target_weight: Optional[float] = None
    position_type: Optional[str] = None


class SliceResponse(SliceBase, UUIDMixin, TimestampMixin):
    """Schema for slice response."""

    pie_id: str
    current_shares: float
    average_cost: Optional[float] = None


# ============================================================================
# Build Rule Schemas
# ============================================================================


class BuildRuleBase(BaseSchema):
    """Base build rule schema."""

    trigger_type: str
    parameters: dict = {}
    is_active: bool = True


class BuildRuleCreate(BuildRuleBase):
    """Schema for creating a build rule."""

    slice_id: str


class BuildRuleUpdate(BaseSchema):
    """Schema for updating a build rule."""

    parameters: Optional[dict] = None
    is_active: Optional[bool] = None


class BuildRuleResponse(BuildRuleBase, UUIDMixin, TimestampMixin):
    """Schema for build rule response."""

    slice_id: str
    last_triggered_at: Optional[datetime] = None


# ============================================================================
# Deposit Schemas
# ============================================================================


class DepositBase(BaseSchema):
    """Base deposit schema."""

    amount: float
    source: Optional[str] = None


class DepositCreate(DepositBase):
    """Schema for creating a deposit."""

    portfolio_id: str


class DepositResponse(DepositBase, UUIDMixin, TimestampMixin):
    """Schema for deposit response."""

    portfolio_id: str
    status: str
    allocated_amount: float
    deposited_at: datetime
    allocated_at: Optional[datetime] = None


# ============================================================================
# Transaction Schemas
# ============================================================================


class TransactionBase(BaseSchema):
    """Base transaction schema."""

    transaction_type: str
    ticker: str
    shares: float
    price: float
    total_amount: float
    commission: float = 0


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction."""

    slice_id: str
    deposit_id: Optional[str] = None
    build_rule_id: Optional[str] = None


class TransactionResponse(TransactionBase, UUIDMixin, TimestampMixin):
    """Schema for transaction response."""

    slice_id: str
    deposit_id: Optional[str] = None
    build_rule_id: Optional[str] = None
    ibkr_order_id: Optional[str] = None
    status: str
    executed_at: Optional[datetime] = None
