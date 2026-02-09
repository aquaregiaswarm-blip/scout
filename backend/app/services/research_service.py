"""Research Service - Orchestrates the multi-agent research flow."""

import uuid
import asyncio
from datetime import datetime, timezone
from typing import Any, AsyncGenerator
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import tables
from app.agents.tools.base import create_default_registry
from app.agents.prime import plan_research, assess_confidence, should_stop_research
from app.agents.researcher import execute_research_paths_parallel
from app.agents.synthesis import synthesize_findings, generate_portfolio_recommendations
from app.models.research import ResearchStatus, FindingCategory

logger = structlog.get_logger()


class ResearchService:
    """Orchestrates the multi-agent research process."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.tool_registry = create_default_registry()
    
    async def run_research(
        self,
        session_id: str,
        event_callback: callable | None = None,
    ) -> None:
        """
        Run a complete research session.
        
        Args:
            session_id: Research session ID
            event_callback: Optional async callback for SSE events
        """
        # Load session with related data
        result = await self.db.execute(
            select(tables.ResearchSession)
            .where(tables.ResearchSession.id == session_id)
            .options(
                selectinload(tables.ResearchSession.initiative)
                .selectinload(tables.Initiative.company_profile)
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            logger.error("Session not found", session_id=session_id)
            return
        
        initiative = session.initiative
        company = initiative.company_profile
        
        logger.info(
            "Starting research session",
            session_id=session_id,
            company=company.company_name,
            initiative=initiative.name,
        )
        
        # Update session status
        session.status = "running"
        session.started_at = datetime.now(timezone.utc)
        await self.db.commit()
        
        await self._emit_event(event_callback, "research_started", {
            "session_id": session_id,
            "company": company.company_name,
            "initiative": initiative.name,
        })
        
        try:
            # Run research cycles
            await self._run_research_cycles(
                session=session,
                initiative=initiative,
                company=company,
                event_callback=event_callback,
            )
            
            # Mark complete
            session.status = "completed"
            session.completed_at = datetime.now(timezone.utc)
            await self.db.commit()
            
            await self._emit_event(event_callback, "research_complete", {
                "session_id": session_id,
            })
            
        except Exception as e:
            logger.error("Research failed", session_id=session_id, error=str(e))
            session.status = "failed"
            session.error_message = str(e)
            session.completed_at = datetime.now(timezone.utc)
            await self.db.commit()
            
            await self._emit_event(event_callback, "error", {
                "session_id": session_id,
                "message": str(e),
            })
    
    async def _run_research_cycles(
        self,
        session: tables.ResearchSession,
        initiative: tables.Initiative,
        company: tables.CompanyProfile,
        event_callback: callable | None,
    ) -> None:
        """Run the Prime → Research → Synthesis cycle."""
        
        findings_by_category: dict[str, list] = {cat.value: [] for cat in FindingCategory}
        confidence_assessment: dict[str, str] = {cat.value: "none" for cat in FindingCategory}
        
        max_cycles = 5
        
        for cycle_number in range(1, max_cycles + 1):
            logger.info(
                "Starting research cycle",
                cycle=cycle_number,
                session_id=str(session.id),
            )
            
            # Create cycle record
            cycle = tables.ResearchCycle(
                id=str(uuid.uuid4()),
                research_session_id=str(session.id),
                cycle_number=cycle_number,
            )
            self.db.add(cycle)
            await self.db.flush()
            
            await self._emit_event(event_callback, "cycle_started", {
                "cycle_number": cycle_number,
                "session_id": str(session.id),
            })
            
            # 1. Prime Agent plans research
            plan = await plan_research(
                company_name=company.company_name,
                initiative_description=initiative.description or initiative.name,
                industry=company.industry,
                current_findings=findings_by_category,
                current_confidence=confidence_assessment,
                cycle_number=cycle_number,
                follow_up_question=session.follow_up_question,
            )
            
            cycle.prime_agent_plan = plan
            await self.db.flush()
            
            # Check if we should stop
            if not plan.get("should_continue", True):
                logger.info("Prime Agent decided to stop", cycle=cycle_number)
                cycle.completed_at = datetime.now(timezone.utc)
                break
            
            # 2. Execute research paths
            research_paths = plan.get("research_paths", [])
            
            if not research_paths:
                logger.warning("No research paths planned", cycle=cycle_number)
                cycle.completed_at = datetime.now(timezone.utc)
                break
            
            # Create path records and emit events
            for path_def in research_paths:
                path = tables.ResearchPath(
                    id=str(uuid.uuid4()),
                    research_cycle_id=str(cycle.id),
                    assignment_id=path_def.get("id", str(uuid.uuid4())),
                    topic=path_def["topic"],
                    instructions=path_def.get("instructions"),
                    status="active",
                )
                self.db.add(path)
                
                await self._emit_event(event_callback, "subagent_started", {
                    "path_id": str(path.id),
                    "topic": path.topic,
                    "priority": path_def.get("priority", "medium"),
                })
            
            await self.db.flush()
            
            # Execute research in parallel
            path_results = await execute_research_paths_parallel(
                paths=research_paths,
                company_name=company.company_name,
                tool_registry=self.tool_registry,
            )
            
            # Process results
            new_findings = []
            tangential_signals = []
            
            for result in path_results:
                path_id = result.get("path_id")
                
                # Update path record
                path_result = await self.db.execute(
                    select(tables.ResearchPath).where(
                        tables.ResearchPath.assignment_id == path_id
                    )
                )
                path_record = path_result.scalar_one_or_none()
                
                if path_record:
                    path_record.status = "completed" if result["status"] == "completed" else "error"
                    path_record.completed_at = datetime.now(timezone.utc)
                    path_record.tools_used = result.get("turns", 0)
                    path_record.reasoning = result.get("error")
                
                # Store findings
                for finding in result.get("findings", []):
                    category = finding.get("category", result.get("category", "initiative"))
                    
                    finding_record = tables.ResearchFinding(
                        id=str(uuid.uuid4()),
                        research_path_id=str(path_record.id) if path_record else None,
                        initiative_id=str(initiative.id),
                        category=category,
                        content=finding,
                        source_url=finding.get("source_url"),
                        source_type="web",
                        confidence_score=finding.get("confidence", 0.5),
                    )
                    self.db.add(finding_record)
                    
                    findings_by_category[category].append(finding)
                    new_findings.append(finding)
                
                tangential_signals.extend(result.get("tangential_signals", []))
                
                await self._emit_event(event_callback, "subagent_completed", {
                    "path_id": path_id,
                    "topic": result.get("topic"),
                    "findings_count": len(result.get("findings", [])),
                    "tangential_signals": result.get("tangential_signals", []),
                })
            
            await self.db.flush()
            
            # 3. Synthesize findings
            synthesis = await synthesize_findings(
                company_name=company.company_name,
                initiative_description=initiative.description or initiative.name,
                findings_by_category=findings_by_category,
            )
            
            # 4. Update confidence assessment
            confidence_assessment = await assess_confidence(
                findings_by_category=findings_by_category,
                previous_assessment=confidence_assessment,
            )
            cycle.confidence_assessment = confidence_assessment
            cycle.completed_at = datetime.now(timezone.utc)
            
            # 5. Update dashboard content
            await self._update_dashboard(
                initiative=initiative,
                synthesis=synthesis,
                confidence=confidence_assessment,
                event_callback=event_callback,
            )
            
            await self.db.commit()
            
            await self._emit_event(event_callback, "synthesis_complete", {
                "cycle_number": cycle_number,
                "new_findings": len(new_findings),
                "confidence": confidence_assessment,
            })
            
            # Check if we should stop based on confidence
            if should_stop_research(confidence_assessment, cycle_number):
                logger.info(
                    "Stopping research - confidence threshold reached",
                    cycle=cycle_number,
                    confidence=confidence_assessment,
                )
                break
            
            # Handle tangential initiatives
            for signal in tangential_signals[:3]:  # Limit to 3
                await self._maybe_create_initiative(
                    company=company,
                    signal=signal,
                    event_callback=event_callback,
                )
    
    async def _update_dashboard(
        self,
        initiative: tables.Initiative,
        synthesis: dict,
        confidence: dict[str, str],
        event_callback: callable | None,
    ) -> None:
        """Update or create dashboard content."""
        
        # Get existing dashboard
        result = await self.db.execute(
            select(tables.DashboardContent).where(
                tables.DashboardContent.initiative_id == str(initiative.id)
            )
        )
        dashboard = result.scalar_one_or_none()
        
        # Build content structure
        categories = synthesis.get("categories", {})
        content = {}
        
        for cat in FindingCategory:
            cat_name = cat.value
            cat_data = categories.get(cat_name, {})
            
            content[cat_name] = {
                "summary": cat_data.get("summary", ""),
                "findings": cat_data.get("findings", []),
                "insights": cat_data.get("insights", []),
                "confidence": confidence.get(cat_name, "none"),
                **{k: v for k, v in cat_data.items() if k not in ("summary", "findings", "insights", "confidence")},
            }
        
        # Get portfolio recommendations
        portfolio_result = await self.db.execute(
            select(tables.PortfolioItem).where(
                tables.PortfolioItem.team_id == initiative.company_profile.team_id
            )
        )
        portfolio_items = [
            {
                "vendor_name": p.vendor_name,
                "partnership_level": p.partnership_level,
                "capabilities": p.capabilities,
            }
            for p in portfolio_result.scalars().all()
        ]
        
        recommendations = await generate_portfolio_recommendations(synthesis, portfolio_items)
        
        if dashboard:
            dashboard.content = content
            dashboard.portfolio_recommendations = recommendations
            dashboard.updated_at = datetime.now(timezone.utc)
        else:
            dashboard = tables.DashboardContent(
                id=str(uuid.uuid4()),
                initiative_id=str(initiative.id),
                content=content,
                portfolio_recommendations=recommendations,
            )
            self.db.add(dashboard)
        
        await self.db.flush()
        
        await self._emit_event(event_callback, "findings_updated", {
            "initiative_id": str(initiative.id),
            "dashboard_content": {
                "id": str(dashboard.id),
                "initiative_id": str(dashboard.initiative_id),
                "content": content,
                "portfolio_recommendations": recommendations,
            },
        })
    
    async def _maybe_create_initiative(
        self,
        company: tables.CompanyProfile,
        signal: str,
        event_callback: callable | None,
    ) -> None:
        """Maybe create a new initiative from a tangential signal."""
        # Simple heuristic - create if signal is substantial
        if len(signal) < 30:
            return
        
        # Check if similar initiative exists
        result = await self.db.execute(
            select(tables.Initiative).where(
                tables.Initiative.company_profile_id == str(company.id),
                tables.Initiative.discovered_by_agent == True,
            )
        )
        existing = result.scalars().all()
        
        # Limit discovered initiatives
        if len(existing) >= 5:
            return
        
        # Create new initiative
        initiative = tables.Initiative(
            id=str(uuid.uuid4()),
            company_profile_id=str(company.id),
            name=signal[:100],
            description=signal,
            discovered_by_agent=True,
        )
        self.db.add(initiative)
        await self.db.flush()
        
        await self._emit_event(event_callback, "initiative_discovered", {
            "initiative_id": str(initiative.id),
            "initiative_name": initiative.name,
            "description": signal,
        })
    
    async def _emit_event(
        self,
        callback: callable | None,
        event_type: str,
        data: dict,
    ) -> None:
        """Emit an SSE event."""
        if callback is None:
            return
        
        event = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **data,
        }
        
        try:
            await callback(event)
        except Exception as e:
            logger.warning("Event callback failed", event_type=event_type, error=str(e))
