"""
Health endpoint tests.
"""

import pytest


def test_health_check(client):
    """Test basic health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_liveness_check(client):
    """Test liveness check endpoint."""
    response = client.get("/api/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
