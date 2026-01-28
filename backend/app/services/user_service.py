"""
User Service

Business logic for user operations.
"""

from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.base import UserResponse, UserUpdate


class UserService:
    """Service class for user-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.

        Args:
            user_id: The user's UUID

        Returns:
            The user if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by their email address.

        Args:
            email: The user's email

        Returns:
            The user if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def update(self, user_id: str, data: UserUpdate) -> Optional[User]:
        """
        Update a user's profile.

        Args:
            user_id: The user's UUID
            data: The update data

        Returns:
            The updated user if found, None otherwise
        """
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            # Nothing to update, just return the user
            return await self.get_by_id(user_id)

        await self.db.execute(
            update(User).where(User.id == user_id).values(**update_data)
        )
        await self.db.commit()

        return await self.get_by_id(user_id)

    async def set_ibkr_connected(self, user_id: str, connected: bool) -> Optional[User]:
        """
        Update a user's IBKR connection status.

        Args:
            user_id: The user's UUID
            connected: Whether IBKR is connected

        Returns:
            The updated user if found, None otherwise
        """
        await self.db.execute(
            update(User).where(User.id == user_id).values(ibkr_connected=connected)
        )
        await self.db.commit()

        return await self.get_by_id(user_id)


async def get_user_service(db: AsyncSession) -> UserService:
    """Factory function to create a UserService instance."""
    return UserService(db)
