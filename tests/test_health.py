"""Tests for the health check endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Health check should return status ok and version."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_version_format(client):
    """Health check version should be a semver string."""
    response = await client.get("/health")
    data = response.json()
    parts = data["version"].split(".")
    assert len(parts) == 3, "Version should be in semver format (x.y.z)"
