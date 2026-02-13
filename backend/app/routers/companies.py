"""Companies API endpoints."""

import uuid
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import structlog

from app.db.database import get_db
from app.db import tables
from app.models.companies import (
    CompanyProfileResponse,
    InitiativeResponse,
    CompanyListResponse,
)
from app.models.research import StartResearchResponse, ResearchStatus

logger = structlog.get_logger()
router = APIRouter()


def _initiative_to_response(initiative: tables.Initiative) -> InitiativeResponse:
    """Convert ORM initiative to response model."""
    return InitiativeResponse(
        id=str(initiative.id),
        company_profile_id=str(initiative.company_profile_id),
        name=initiative.name,
        description=initiative.description,
        discovered_by_agent=initiative.discovered_by_agent,
        created_at=initiative.created_at,
        updated_at=initiative.updated_at,
    )


def _company_to_response(company: tables.CompanyProfile) -> CompanyProfileResponse:
    """Convert ORM company to response model."""
    return CompanyProfileResponse(
        id=str(company.id),
        team_id=str(company.team_id),
        company_name=company.company_name,
        industry=company.industry,
        created_at=company.created_at,
        updated_at=company.updated_at,
        initiatives=[_initiative_to_response(i) for i in (company.initiatives or [])],
    )


@router.get("", response_model=CompanyListResponse)
async def list_companies(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List all companies for the current team."""
    # Placeholder team_id - will use auth when implemented
    team_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

    # Get total count
    count_result = await db.execute(
        select(func.count(tables.CompanyProfile.id)).where(
            tables.CompanyProfile.team_id == team_id
        )
    )
    total = count_result.scalar() or 0

    # Get companies with initiatives
    result = await db.execute(
        select(tables.CompanyProfile)
        .where(tables.CompanyProfile.team_id == team_id)
        .options(selectinload(tables.CompanyProfile.initiatives))
        .order_by(tables.CompanyProfile.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    companies = result.scalars().all()

    return CompanyListResponse(
        data=[_company_to_response(c) for c in companies],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{company_id}", response_model=CompanyProfileResponse)
async def get_company(
    company_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a company by ID."""
    result = await db.execute(
        select(tables.CompanyProfile)
        .where(tables.CompanyProfile.id == company_id)
        .options(selectinload(tables.CompanyProfile.initiatives))
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return _company_to_response(company)


@router.get("/{company_id}/initiatives", response_model=list[InitiativeResponse])
async def get_company_initiatives(
    company_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all initiatives for a company."""
    result = await db.execute(
        select(tables.Initiative)
        .where(tables.Initiative.company_profile_id == company_id)
        .order_by(tables.Initiative.updated_at.desc())
    )
    initiatives = result.scalars().all()

    return [_initiative_to_response(i) for i in initiatives]


@router.delete("/{company_id}")
async def delete_company(
    company_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a company and all its data."""
    result = await db.execute(
        select(tables.CompanyProfile).where(tables.CompanyProfile.id == company_id)
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    await db.delete(company)
    await db.commit()

    return {"status": "deleted"}


@router.post(
    "/{company_id}/initiatives/{initiative_id}/refresh",
    response_model=StartResearchResponse,
)
async def refresh_initiative(
    company_id: str,
    initiative_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Start a refresh research session for an initiative."""
    result = await db.execute(
        select(tables.Initiative).where(tables.Initiative.id == initiative_id)
    )
    initiative = result.scalar_one_or_none()

    if not initiative or str(initiative.company_profile_id) != company_id:
        raise HTTPException(status_code=404, detail="Initiative not found")

    # Create new research session
    session = tables.ResearchSession(
        id=str(uuid.uuid4()),
        initiative_id=str(initiative.id),
        triggered_by="refresh",
        status="pending",
    )
    db.add(session)
    await db.commit()

    return StartResearchResponse(
        session_id=str(session.id),
        status=ResearchStatus.PENDING,
        initiative_id=str(initiative.id),
    )


@router.get("/initiatives/{initiative_id}/dashboard")
async def get_initiative_dashboard(
    initiative_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the dashboard content for an initiative."""
    result = await db.execute(
        select(tables.DashboardContent).where(
            tables.DashboardContent.initiative_id == initiative_id
        )
    )
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    return {
        "id": str(dashboard.id),
        "initiative_id": str(dashboard.initiative_id),
        "content": dashboard.content,
        "portfolio_recommendations": dashboard.portfolio_recommendations,
        "created_at": dashboard.created_at,
        "updated_at": dashboard.updated_at,
    }
