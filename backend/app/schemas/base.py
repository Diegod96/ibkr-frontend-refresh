"""
Base Schemas

Common schema patterns and base classes.
"""

from datetime import datetime

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
    display_name: str | None = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    pass


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    display_name: str | None = None
    ibkr_connected: bool | None = None


class UserResponse(UserBase, UUIDMixin, TimestampMixin):
    """Schema for user response."""

    ibkr_connected: bool


# ============================================================================
# Portfolio Schemas
# ============================================================================


class PortfolioBase(BaseSchema):
    """Base portfolio schema."""

    name: str
    description: str | None = None
    account_type: str | None = None
    ibkr_account_id: str | None = None
    auto_invest_enabled: bool = False


class PortfolioCreate(PortfolioBase):
    """Schema for creating a portfolio."""

    pass


class PortfolioUpdate(BaseSchema):
    """Schema for updating a portfolio."""

    name: str | None = None
    description: str | None = None
    account_type: str | None = None
    ibkr_account_id: str | None = None
    auto_invest_enabled: bool | None = None


class PortfolioResponse(PortfolioBase, UUIDMixin, TimestampMixin):
    """Schema for portfolio response."""

    user_id: str


# ============================================================================
# Pie Schemas
# ============================================================================


class PieBase(BaseSchema):
    """Base pie schema."""

    name: str
    description: str | None = None
    target_weight: float
    color: str | None = None


class PieCreate(PieBase):
    """Schema for creating a pie."""

    portfolio_id: str


class PieUpdate(BaseSchema):
    """Schema for updating a pie."""

    name: str | None = None
    description: str | None = None
    target_weight: float | None = None
    color: str | None = None


class PieResponse(PieBase, UUIDMixin, TimestampMixin):
    """Schema for pie response."""

    portfolio_id: str


# ============================================================================
# Slice Schemas
# ============================================================================


class SliceBase(BaseSchema):
    """Base slice schema."""

    ticker: str
    name: str | None = None
    target_weight: float
    position_type: str = "full"


class SliceCreate(SliceBase):
    """Schema for creating a slice."""

    pie_id: str


class SliceUpdate(BaseSchema):
    """Schema for updating a slice."""

    name: str | None = None
    target_weight: float | None = None
    position_type: str | None = None


class SliceResponse(SliceBase, UUIDMixin, TimestampMixin):
    """Schema for slice response."""

    pie_id: str
    current_shares: float
    average_cost: float | None = None


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

    parameters: dict | None = None
    is_active: bool | None = None


class BuildRuleResponse(BuildRuleBase, UUIDMixin, TimestampMixin):
    """Schema for build rule response."""

    slice_id: str
    last_triggered_at: datetime | None = None


# ============================================================================
# Deposit Schemas
# ============================================================================


class DepositBase(BaseSchema):
    """Base deposit schema."""

    amount: float
    source: str | None = None


class DepositCreate(DepositBase):
    """Schema for creating a deposit."""

    portfolio_id: str


class DepositResponse(DepositBase, UUIDMixin, TimestampMixin):
    """Schema for deposit response."""

    portfolio_id: str
    status: str
    allocated_amount: float
    deposited_at: datetime
    allocated_at: datetime | None = None


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
    deposit_id: str | None = None
    build_rule_id: str | None = None


class TransactionResponse(TransactionBase, UUIDMixin, TimestampMixin):
    """Schema for transaction response."""

    slice_id: str
    deposit_id: str | None = None
    build_rule_id: str | None = None
    ibkr_order_id: str | None = None
    status: str
    executed_at: datetime | None = None
