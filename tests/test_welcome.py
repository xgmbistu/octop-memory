"""Contract tests for the native GET /welcome route."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi", reason="dashboard extra not installed")

from fastapi.testclient import TestClient

from octop_memory.adapters.dashboard.server import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestWelcome:
    def test_welcome_returns_message(self, client: TestClient) -> None:
        res = client.get("/welcome")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("application/json")
        assert res.json() == {"message": "welcome"}
        assert res.json()["message"] == "welcome"
