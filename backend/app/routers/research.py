"""Research API endpoints."""

import uuid
import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
import json

from app.db.database import get_db, AsyncSessionLocal
from app.db import tables
from app.models.research import (
    StartResearchRequest,
    StartResearchResponse,
    FollowUpRequest,
    ResearchSessionResponse,
    DashboardContentResponse,
    ResearchStatus,
)
from app.services.research_service import ResearchService
from app.streams.sse import sse_manager, create_event_callback, format_sse_message

logger = structlog.get_logger()
router = APIRouter()


@router.post("/start", response_model=StartResearchResponse)
async def start_research(
    request: StartResearchRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Start a new research session."""
    logger.info(
        "Starting research",
        company=request.company_name,
        initiative=request.initiative_description[:50],
    )

    # Get or create team (placeholder - will use auth)
    team_id = "default-team"

    # Get or create company profile
    result = await db.execute(
        select(tables.CompanyProfile).where(
            tables.CompanyProfile.team_id == team_id,
            tables.CompanyProfile.company_name == request.company_name,
        )
    )
    company = result.scalar_one_or_none()

    if not company:
        company = tables.CompanyProfile(
            id=str(uuid.uuid4()),
            team_id=team_id,
            company_name=request.company_name,
            industry=request.industry,
        )
        db.add(company)
        await db.flush()

    # Create initiative
    initiative = tables.Initiative(
        id=str(uuid.uuid4()),
        company_profile_id=company.id,
        name=request.initiative_description[:100],
        description=request.initiative_description,
        discovered_by_agent=False,
    )
    db.add(initiative)
    await db.flush()

    # Create research session
    session = tables.ResearchSession(
        id=str(uuid.uuid4()),
        initiative_id=initiative.id,
        triggered_by="user",
        status="pending",
    )
    db.add(session)
    await db.commit()

    # Start research in background
    async def run_research_task():
        """Run research with a new database session."""
        async with AsyncSessionLocal() as task_db:
            service = ResearchService(task_db)
            event_callback = await create_event_callback(session.id)
            await service.run_research(session.id, event_callback)
    
    background_tasks.add_task(asyncio.create_task, run_research_task())

    return StartResearchResponse(
        session_id=session.id,
        status=ResearchStatus.PENDING,
        initiative_id=initiative.id,
    )


@router.get("/{session_id}", response_model=ResearchSessionResponse)
async def get_research_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get research session details."""
    result = await db.execute(
        select(tables.ResearchSession).where(tables.ResearchSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return ResearchSessionResponse(
        id=session.id,
        initiative_id=session.initiative_id,
        triggered_by=session.triggered_by,
        status=ResearchStatus(session.status),
        follow_up_question=session.follow_up_question,
        started_at=session.started_at,
        completed_at=session.completed_at,
        error_message=session.error_message,
    )


@router.post("/{session_id}/stop")
async def stop_research(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Stop an active research session."""
    result = await db.execute(
        select(tables.ResearchSession).where(tables.ResearchSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status not in ("pending", "running"):
        raise HTTPException(status_code=400, detail="Session is not active")

    session.status = "stopped"
    session.completed_at = datetime.now(timezone.utc)
    await db.commit()

    return {"status": "stopped"}


@router.post("/{session_id}/paths/{path_id}/stop")
async def stop_research_path(
    session_id: str,
    path_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Stop a specific research path."""
    result = await db.execute(
        select(tables.ResearchPath).where(tables.ResearchPath.id == path_id)
    )
    path = result.scalar_one_or_none()

    if not path:
        raise HTTPException(status_code=404, detail="Path not found")

    if path.status != "active":
        raise HTTPException(status_code=400, detail="Path is not active")

    path.status = "stopped"
    path.completed_at = datetime.now(timezone.utc)
    await db.commit()

    return {"status": "stopped"}


@router.post("/{session_id}/follow-up", response_model=StartResearchResponse)
async def follow_up_research(
    session_id: str,
    request: FollowUpRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Start a follow-up research session."""
    result = await db.execute(
        select(tables.ResearchSession).where(tables.ResearchSession.id == session_id)
    )
    original_session = result.scalar_one_or_none()

    if not original_session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Create new session for follow-up
    new_session = tables.ResearchSession(
        id=str(uuid.uuid4()),
        initiative_id=original_session.initiative_id,
        triggered_by="follow_up",
        status="pending",
        follow_up_question=request.question,
    )
    db.add(new_session)
    await db.commit()

    # Start research in background
    # background_tasks.add_task(
    #     ResearchService(db).run_research,
    #     new_session.id,
    # )

    return StartResearchResponse(
        session_id=new_session.id,
        status=ResearchStatus.PENDING,
        initiative_id=original_session.initiative_id,
    )


@router.get("/{session_id}/stream")
async def stream_research(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Stream research events via SSE."""
    
    # Verify session exists
    result = await db.execute(
        select(tables.ResearchSession).where(tables.ResearchSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events."""
        # Subscribe to session events
        queue = await sse_manager.subscribe(session_id)
        
        try:
            # Send connected event
            yield format_sse_message({
                "type": "connected",
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            
            # Stream events from queue
            timeout = 300  # 5 minutes max
            start_time = asyncio.get_event_loop().time()
            
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= timeout:
                    break
                
                try:
                    # Wait for event with timeout for heartbeat
                    event = await asyncio.wait_for(queue.get(), timeout=30)
                    yield format_sse_message(event)
                    
                    # Check if research is complete
                    if event.get("type") in ("research_complete", "error"):
                        break
                        
                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield format_sse_message({
                        "type": "heartbeat",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
        
        finally:
            await sse_manager.unsubscribe(session_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
