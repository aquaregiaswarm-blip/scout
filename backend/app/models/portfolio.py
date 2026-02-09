"""Portfolio-related Pydantic models."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PortfolioItemCreate(BaseModel):
    """Request to create a portfolio item."""
    vendor_name: str = Field(..., min_length=1, max_length=200)
    partnership_level: Optional[str] = Field(None, max_length=50)
    capabilities: Optional[list[str]] = None


class PortfolioItemUpdate(BaseModel):
    """Request to update a portfolio item."""
    vendor_name: Optional[str] = Field(None, min_length=1, max_length=200)
    partnership_level: Optional[str] = Field(None, max_length=50)
    capabilities: Optional[list[str]] = None


class PortfolioItemResponse(BaseModel):
    """Portfolio item response."""
    id: str
    team_id: str
    vendor_name: str
    partnership_level: Optional[str] = None
    capabilities: Optional[list[str]] = None
    created_at: datetime
    updated_at: datetime


class PortfolioBulkImport(BaseModel):
    """Bulk import request."""
    items: list[PortfolioItemCreate]
