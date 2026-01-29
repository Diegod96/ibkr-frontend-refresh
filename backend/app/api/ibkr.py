"""
IBKR API Routes

Endpoints for interacting with IBKR Client Portal Gateway.
"""

from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import CurrentUserId
from app.services.ibkr.client import IBKRClient

router = APIRouter()


class IBKRStatusResponse(BaseModel):
    """IBKR connection status response."""

    authenticated: bool
    connected: bool
    message: str
    details: dict[str, Any] | None = None


class IBKRAccountResponse(BaseModel):
    """IBKR account information."""

    account_id: str
    account_title: str | None = None
    account_type: str | None = None


@router.get("/status", response_model=IBKRStatusResponse)
async def get_ibkr_status(
    user_id: CurrentUserId,
) -> IBKRStatusResponse:
    """
    Check IBKR Gateway connection and authentication status.

    Returns whether the gateway is running and if the user is authenticated.
    """
    client = IBKRClient()

    try:
        # Check if gateway is reachable and authenticated
        status_response = await client.check_auth_status()

        # IBKR returns authenticated: true/false
        authenticated = status_response.get("authenticated", False)
        connected = True

        return IBKRStatusResponse(
            authenticated=authenticated,
            connected=connected,
            message="Connected to IBKR Gateway" if authenticated else "Gateway connected but not authenticated",
            details=status_response,
        )
    except httpx.ConnectError as e:
        return IBKRStatusResponse(
            authenticated=False,
            connected=False,
            message=f"Cannot connect to Client Portal Gateway at {client.host}:{client.port}. Make sure the Client Portal Gateway (not IB Gateway) is running. Download from: https://www.interactivebrokers.com/en/trading/ib-api.php",
            details={
                "error_type": "ConnectError",
                "error": str(e),
                "host": client.host,
                "port": client.port,
                "note": "This is different from IB Gateway desktop app. You need the Client Portal Gateway Java application.",
            },
        )
    except (httpx.TimeoutException, httpx.ConnectTimeout, httpx.ReadTimeout) as e:
        return IBKRStatusResponse(
            authenticated=False,
            connected=False,
            message=f"Connection to IBKR Gateway timed out at {client.host}:{client.port}",
            details={"error_type": "Timeout", "error": str(e)},
        )
    except httpx.HTTPStatusError as e:
        # Gateway is reachable but returned an error status
        return IBKRStatusResponse(
            authenticated=False,
            connected=True,
            message=f"Gateway responded with error: {e.response.status_code}",
            details={
                "status_code": e.response.status_code,
                "error": str(e),
                "response_text": e.response.text[:200] if hasattr(e.response, "text") else None,
            },
        )
    except httpx.HTTPError as e:
        # Other HTTP errors
        return IBKRStatusResponse(
            authenticated=False,
            connected=True,
            message=f"HTTP error connecting to gateway: {str(e)}",
            details={"error_type": "HTTPError", "error": str(e)},
        )
    except Exception as e:
        return IBKRStatusResponse(
            authenticated=False,
            connected=False,
            message=f"Error checking IBKR status: {str(e)}",
            details={"error_type": type(e).__name__, "error": str(e)},
        )


@router.get("/accounts", response_model=list[IBKRAccountResponse])
async def get_ibkr_accounts(
    user_id: CurrentUserId,
) -> list[IBKRAccountResponse]:
    """
    Get list of available IBKR accounts.

    Requires authentication with IBKR Gateway.
    """
    client = IBKRClient()

    try:
        # First check if authenticated
        status_response = await client.check_auth_status()
        if not status_response.get("authenticated", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated with IBKR Gateway. Please login through the gateway first.",
            )

        # Get accounts
        accounts_data = await client.get_accounts()

        # Transform to response model
        accounts = []
        for account in accounts_data:
            # IBKR returns accountId as key or in accountId field
            account_id = account.get("accountId") or account.get("id") or str(account)
            accounts.append(
                IBKRAccountResponse(
                    account_id=account_id,
                    account_title=account.get("accountTitle"),
                    account_type=account.get("accountType"),
                )
            )

        return accounts
    except HTTPException:
        raise
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot connect to IBKR Gateway. Make sure the Client Portal Gateway is running.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching IBKR accounts: {str(e)}",
        )
