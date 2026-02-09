"""Tests for health check endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test the health check endpoint returns 200."""
    response = await client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "Scout"


@pytest.mark.asyncio
async def test_readiness_endpoint(client: AsyncClient):
    """Test the readiness check endpoint returns 200."""
    response = await client.get("/api/v1/health/ready")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "checks" in data
