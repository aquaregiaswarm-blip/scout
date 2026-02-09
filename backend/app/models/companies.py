"""Company-related Pydantic models."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class InitiativeResponse(BaseModel):
    """Initiative details."""
    id: str
    company_profile_id: str
    name: str
    description: Optional[str] = None
    discovered_by_agent: bool = False
    created_at: datetime
    updated_at: datetime


class CompanyProfileResponse(BaseModel):
    """Company profile with initiatives."""
    id: str
    team_id: str
    company_name: str
    industry: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    initiatives: list[InitiativeResponse] = Field(default_factory=list)


class CompanyListResponse(BaseModel):
    """Paginated list of companies."""
    data: list[CompanyProfileResponse]
    total: int
    offset: int
    limit: int
