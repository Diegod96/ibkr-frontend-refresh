"""
IBKR Client

HTTP client for interacting with IBKR Client Portal Gateway API.
"""

import httpx
from typing import Any

from app.core.config import settings


class IBKRClient:
    """
    Client for IBKR Client Portal Gateway API.

    The gateway runs locally and proxies requests to IBKR servers
    with appropriate authentication.
    """

    def __init__(self, host: str | None = None, port: int | None = None):
        """
        Initialize IBKR client.

        Args:
            host: Gateway host (defaults to config)
            port: Gateway port (defaults to config)
        """
        self.host = host or settings.ibkr_gateway_host
        self.port = port or settings.ibkr_gateway_port
        self.base_url = f"https://{self.host}:{self.port}/v1/api"

    async def _request(
        self, method: str, endpoint: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the IBKR Gateway.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (without /v1/api prefix)
            data: Optional request body data

        Returns:
            JSON response as dictionary

        Raises:
            httpx.HTTPError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        # Gateway uses self-signed SSL cert, so we disable verification
        # Use shorter timeout for status checks to avoid blocking
        timeout = httpx.Timeout(5.0, connect=2.0)
        async with httpx.AsyncClient(verify=False, timeout=timeout) as client:
            if method.upper() == "GET":
                response = await client.get(url)
            elif method.upper() == "POST":
                response = await client.post(url, json=data or {})
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()

    async def check_auth_status(self) -> dict[str, Any]:
        """
        Check authentication status with IBKR.

        Returns:
            Status response indicating if user is authenticated
        """
        return await self._request("POST", "/iserver/auth/status")

    async def init_brokerage_session(self) -> dict[str, Any]:
        """
        Initialize brokerage session for trading and market data access.

        This is the second-tier authentication required for trading operations.

        Returns:
            Session initialization response
        """
        return await self._request("POST", "/iserver/auth/ssodh/init")

    async def get_accounts(self) -> list[dict[str, Any]]:
        """
        Get list of available IBKR accounts.

        Returns:
            List of account information dictionaries
        """
        response = await self._request("GET", "/portfolio/accounts")
        # API returns list directly or wrapped in accounts key
        if isinstance(response, list):
            return response
        return response.get("accounts", [])
