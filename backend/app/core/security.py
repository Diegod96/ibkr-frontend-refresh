"""
Security Module

JWT verification and authentication utilities for Supabase Auth integration.
"""

from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings


class AuthError(HTTPException):
    """Authentication error exception."""

    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_supabase_token(token: str) -> dict[str, Any]:
    """
    Verify a Supabase JWT token.

    Supabase JWTs are signed with the project's JWT secret.
    The token contains the user's ID in the 'sub' claim.

    Args:
        token: The JWT token to verify

    Returns:
        The decoded token payload

    Raises:
        AuthError: If the token is invalid or expired
    """
    try:
        # Supabase uses HS256 algorithm with the JWT secret
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience="authenticated",
        )

        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise AuthError("Token has expired")

        # Ensure we have a user ID
        user_id = payload.get("sub")
        if not user_id:
            raise AuthError("Token missing user ID")

        return payload

    except JWTError as e:
        raise AuthError(f"Invalid token: {str(e)}") from e


def extract_user_id_from_token(token: str) -> str:
    """
    Extract the user ID from a Supabase JWT token.

    Args:
        token: The JWT token

        Returns:
            The user's ID as a 36-character string

    Raises:
        AuthError: If the token is invalid or doesn't contain a user ID
    """
    payload = verify_supabase_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise AuthError("Token missing user ID")
    return user_id


def get_token_from_header(authorization: str | None) -> str:
    """
    Extract the token from an Authorization header.

    Args:
        authorization: The Authorization header value (e.g., "Bearer <token>")

    Returns:
        The extracted token

    Raises:
        AuthError: If the header is missing or malformed
    """
    if not authorization:
        raise AuthError("Missing authorization header")

    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthError("Invalid authorization header format. Expected 'Bearer <token>'")

    return parts[1]
