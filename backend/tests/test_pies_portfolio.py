"""
Tests for pie portfolio scoping and allocation rules.
"""

import pytest




def _override_user(user_id_str: str, app):
    from app.api.deps import get_current_user_id

    def _fake_current_user():
        # get_current_user_id now returns a string ID
        return user_id_str

    app.dependency_overrides[get_current_user_id] = _fake_current_user


def _clear_overrides(app):
    from app.api.deps import get_current_user_id

    app.dependency_overrides.pop(get_current_user_id, None)


def test_create_pie_uses_default_portfolio(client):
    # Use a stable test UUID
    test_user = "11111111-2222-3333-4444-555555555555"
    _override_user(test_user, client.app)

    # Create a pie without providing portfolio_id
    resp = client.post("/api/pies", json={"name": "DefaultPie", "target_allocation": 5})
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["name"] == "DefaultPie"
    assert data["portfolio_id"] is not None

    _clear_overrides(client.app)


def test_create_pie_with_explicit_portfolio_and_ownership(client):
    test_user = "22222222-3333-4444-5555-666666666666"
    _override_user(test_user, client.app)

    # Create a portfolio for this user
    resp = client.post("/api/portfolios", json={"name": "Owned Portfolio"})
    assert resp.status_code == 201, resp.text
    portfolio = resp.json()

    # Create a pie in that portfolio
    resp2 = client.post(
        "/api/pies",
        json={"name": "OwnedPie", "target_allocation": 10, "portfolio_id": portfolio["id"]},
    )
    assert resp2.status_code == 201, resp2.text
    pie = resp2.json()
    assert pie["portfolio_id"] == portfolio["id"]

    _clear_overrides(client.app)


def test_create_pie_with_other_users_portfolio_forbidden(client):
    # Create a portfolio under user A
    user_a = "33333333-4444-5555-6666-777777777777"
    _override_user(user_a, client.app)
    resp = client.post("/api/portfolios", json={"name": "UserAPortfolio"})
    assert resp.status_code == 201, resp.text
    portfolio = resp.json()
    _clear_overrides(client.app)

    # Try to create a pie under that portfolio as user B
    user_b = "44444444-5555-6666-7777-888888888888"
    _override_user(user_b, client.app)
    resp2 = client.post(
        "/api/pies",
        json={"name": "BadPie", "target_allocation": 5, "portfolio_id": portfolio["id"]},
    )
    assert resp2.status_code == 403

    _clear_overrides(client.app)
