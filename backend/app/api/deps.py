"""
API Dependencies

FastAPI dependencies for authentication and authorization.
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import AuthError, extract_user_id_from_token, get_token_from_header
from app.schemas.base import UserResponse


async def get_current_user_id(
    authorization: Annotated[Optional[str], Header()] = None,
) -> str:
    """
    Dependency to extract and validate the current user's ID from the JWT token.

    Args:
        authorization: The Authorization header containing the Bearer token

    Returns:
        The user's UUID

    Raises:
        AuthError: If authentication fails
    """
    token = get_token_from_header(authorization)
    user_id_str = extract_user_id_from_token(token)
    try:
        # validate UUID format but return string so services and DB use string IDs consistently
        _ = UUID(user_id_str)
        return user_id_str
    except ValueError:
        raise AuthError("Invalid user ID in token")


async def get_current_user(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    Dependency to get the current authenticated user from the database.

    Args:
        user_id: The user's UUID from the JWT token
        db: Database session

    Returns:
        The user data

    Raises:
        AuthError: If the user is not found in the database
    """
    from app.models.user import User  # Import here to avoid circular imports

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthError("User not found")

    return UserResponse.model_validate(user)


async def get_optional_user(
    authorization: Annotated[Optional[str], Header()] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> Optional[UserResponse]:
    """
    Dependency to optionally get the current user if authenticated.

    This is useful for endpoints that work differently for authenticated
    vs unauthenticated users.

    Args:
        authorization: The Authorization header (optional)
        db: Database session

    Returns:
        The user data if authenticated, None otherwise
    """
    if not authorization:
        return None

    try:
        token = get_token_from_header(authorization)
        user_id_str = extract_user_id_from_token(token)
        user_id = user_id_str

        from app.models.user import User

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user:
            return UserResponse.model_validate(user)
        return None

    except (AuthError, ValueError):
        return None


# Type aliases for cleaner dependency injection
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
CurrentUser = Annotated[UserResponse, Depends(get_current_user)]
OptionalUser = Annotated[Optional[UserResponse], Depends(get_optional_user)]
