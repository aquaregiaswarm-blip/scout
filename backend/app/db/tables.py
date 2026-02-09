"""SQLAlchemy ORM table definitions."""

from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum
import uuid

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float,
    ForeignKey, DateTime, Enum, Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.database import Base


# Enums
class ResearchStatus(str, PyEnum):
    """Status of a research session."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED = "stopped"
    FAILED = "failed"


class PathStatus(str, PyEnum):
    """Status of a research path (sub-agent)."""
    ACTIVE = "active"
    COMPLETED = "completed"
    STOPPED = "stopped"
    EXHAUSTED = "exhausted"
    ERROR = "error"


class FindingCategory(str, PyEnum):
    """Category of a research finding."""
    PEOPLE = "people"
    INITIATIVE = "initiative"
    TECHNOLOGY = "technology"
    COMPETITIVE = "competitive"
    FINANCIAL = "financial"
    MARKET = "market"


class ConfidenceLevel(str, PyEnum):
    """Confidence level for intelligence."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SUFFICIENT = "sufficient"


# Tables
class Team(Base):
    """Team/organization that shares research profiles."""
    __tablename__ = "teams"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="team")
    company_profiles: Mapped[list["CompanyProfile"]] = relationship("CompanyProfile", back_populates="team")
    portfolio_items: Mapped[list["PortfolioItem"]] = relationship("PortfolioItem", back_populates="team")


class User(Base):
    """User account."""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="users")
    
    __table_args__ = (
        Index("ix_users_email", "email"),
    )


class CompanyProfile(Base):
    """Target company being researched."""
    __tablename__ = "company_profiles"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="company_profiles")
    initiatives: Mapped[list["Initiative"]] = relationship("Initiative", back_populates="company_profile")
    
    __table_args__ = (
        Index("ix_company_profiles_team", "team_id"),
    )


class Initiative(Base):
    """A specific project or initiative being researched for a company."""
    __tablename__ = "initiatives"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_profile_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("company_profiles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    discovered_by_agent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company_profile: Mapped["CompanyProfile"] = relationship("CompanyProfile", back_populates="initiatives")
    research_sessions: Mapped[list["ResearchSession"]] = relationship("ResearchSession", back_populates="initiative")
    findings: Mapped[list["ResearchFinding"]] = relationship("ResearchFinding", back_populates="initiative")
    synthesized_intelligence: Mapped[list["SynthesizedIntelligence"]] = relationship("SynthesizedIntelligence", back_populates="initiative")
    dashboard_content: Mapped[Optional["DashboardContent"]] = relationship("DashboardContent", back_populates="initiative", uselist=False)


class ResearchSession(Base):
    """A research session - one run of the agent loop."""
    __tablename__ = "research_sessions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    initiative_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("initiatives.id"), nullable=False)
    triggered_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped[ResearchStatus] = mapped_column(Enum(ResearchStatus), default=ResearchStatus.PENDING)
    follow_up_question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    initiative: Mapped["Initiative"] = relationship("Initiative", back_populates="research_sessions")
    cycles: Mapped[list["ResearchCycle"]] = relationship("ResearchCycle", back_populates="session")


class ResearchCycle(Base):
    """A single cycle of the research loop."""
    __tablename__ = "research_cycles"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    research_session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("research_sessions.id"), nullable=False)
    cycle_number: Mapped[int] = mapped_column(Integer, nullable=False)
    prime_agent_plan: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    confidence_assessment: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    session: Mapped["ResearchSession"] = relationship("ResearchSession", back_populates="cycles")
    paths: Mapped[list["ResearchPath"]] = relationship("ResearchPath", back_populates="cycle")


class ResearchPath(Base):
    """A research sub-agent assignment and its execution."""
    __tablename__ = "research_paths"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    research_cycle_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("research_cycles.id"), nullable=False)
    assignment_id: Mapped[str] = mapped_column(String(50), nullable=False)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[PathStatus] = mapped_column(Enum(PathStatus), default=PathStatus.ACTIVE)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tools_used: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    cycle: Mapped["ResearchCycle"] = relationship("ResearchCycle", back_populates="paths")
    findings: Mapped[list["ResearchFinding"]] = relationship("ResearchFinding", back_populates="path")


class ResearchFinding(Base):
    """A single finding from a research sub-agent."""
    __tablename__ = "research_findings"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    research_path_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("research_paths.id"), nullable=False)
    initiative_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("initiatives.id"), nullable=False)
    category: Mapped[FindingCategory] = mapped_column(Enum(FindingCategory), nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    path: Mapped["ResearchPath"] = relationship("ResearchPath", back_populates="findings")
    initiative: Mapped["Initiative"] = relationship("Initiative", back_populates="findings")
    
    __table_args__ = (
        Index("ix_research_findings_initiative", "initiative_id"),
        Index("ix_research_findings_category", "category"),
    )


class SynthesizedIntelligence(Base):
    """Merged and categorized intelligence for an initiative."""
    __tablename__ = "synthesized_intelligence"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    initiative_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("initiatives.id"), nullable=False)
    category: Mapped[FindingCategory] = mapped_column(Enum(FindingCategory), nullable=False)
    structured_content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    last_updated_cycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    initiative: Mapped["Initiative"] = relationship("Initiative", back_populates="synthesized_intelligence")


class DashboardContent(Base):
    """Presentation-ready content for the dashboard."""
    __tablename__ = "dashboard_content"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    initiative_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("initiatives.id"), nullable=False, unique=True)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    portfolio_recommendations: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    initiative: Mapped["Initiative"] = relationship("Initiative", back_populates="dashboard_content")


class PortfolioItem(Base):
    """A vendor partnership or capability in the team's portfolio."""
    __tablename__ = "portfolio_items"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    partnership_level: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    capabilities: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="portfolio_items")
