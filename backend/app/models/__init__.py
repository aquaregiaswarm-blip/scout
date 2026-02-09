"""Pydantic models for request/response validation."""

from .research import (
    StartResearchRequest,
    StartResearchResponse,
    FollowUpRequest,
    ResearchSessionResponse,
    DashboardContentResponse,
)
from .companies import (
    CompanyProfileResponse,
    InitiativeResponse,
    CompanyListResponse,
)
from .portfolio import (
    PortfolioItemCreate,
    PortfolioItemUpdate,
    PortfolioItemResponse,
)
from .auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

__all__ = [
    # Research
    "StartResearchRequest",
    "StartResearchResponse",
    "FollowUpRequest",
    "ResearchSessionResponse",
    "DashboardContentResponse",
    # Companies
    "CompanyProfileResponse",
    "InitiativeResponse",
    "CompanyListResponse",
    # Portfolio
    "PortfolioItemCreate",
    "PortfolioItemUpdate",
    "PortfolioItemResponse",
    # Auth
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "UserResponse",
]
