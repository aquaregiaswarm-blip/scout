"""Research-related Pydantic models."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class ResearchStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED = "stopped"
    FAILED = "failed"


class ConfidenceLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SUFFICIENT = "sufficient"


class FindingCategory(str, Enum):
    PEOPLE = "people"
    INITIATIVE = "initiative"
    TECHNOLOGY = "technology"
    COMPETITIVE = "competitive"
    FINANCIAL = "financial"
    MARKET = "market"


class StartResearchRequest(BaseModel):
    """Request to start a new research session."""
    company_name: str = Field(..., min_length=1, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    initiative_description: str = Field(..., min_length=10, max_length=2000)


class StartResearchResponse(BaseModel):
    """Response after starting research."""
    session_id: str
    status: ResearchStatus
    initiative_id: str


class FollowUpRequest(BaseModel):
    """Request for a follow-up question."""
    question: str = Field(..., min_length=5, max_length=1000)


class ResearchSessionResponse(BaseModel):
    """Full research session details."""
    id: str
    initiative_id: str
    triggered_by: str
    status: ResearchStatus
    follow_up_question: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class ConfidenceAssessment(BaseModel):
    """Confidence levels for each category."""
    people: ConfidenceLevel = ConfidenceLevel.NONE
    initiative: ConfidenceLevel = ConfidenceLevel.NONE
    technology: ConfidenceLevel = ConfidenceLevel.NONE
    competitive: ConfidenceLevel = ConfidenceLevel.NONE
    financial: ConfidenceLevel = ConfidenceLevel.NONE
    market: ConfidenceLevel = ConfidenceLevel.NONE


class CategoryContent(BaseModel):
    """Content for a single category."""
    summary: str
    findings: list = Field(default_factory=list)
    insights: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel


class PortfolioRecommendation(BaseModel):
    """A vendor recommendation based on research."""
    vendor: str
    capability: str
    relevance: str
    supporting_findings: list[str] = Field(default_factory=list)


class DashboardContent(BaseModel):
    """Dashboard content structure."""
    people: Optional[CategoryContent] = None
    initiative: Optional[CategoryContent] = None
    technology: Optional[CategoryContent] = None
    competitive: Optional[CategoryContent] = None
    financial: Optional[CategoryContent] = None
    market: Optional[CategoryContent] = None


class DashboardContentResponse(BaseModel):
    """Full dashboard response."""
    id: str
    initiative_id: str
    content: DashboardContent
    portfolio_recommendations: list[PortfolioRecommendation] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
