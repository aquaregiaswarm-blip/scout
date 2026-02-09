"""Prime Agent - Plans and orchestrates research."""

import json
import structlog
from typing import Any

from app.agents.claude_client import call_claude
from app.models.research import ConfidenceLevel, FindingCategory

logger = structlog.get_logger()

PRIME_SYSTEM_PROMPT = """You are the Prime Agent for Scout, an AI-powered sales intelligence platform.

Your role is to:
1. Analyze the research target (company + initiative)
2. Plan research paths for sub-agents to execute
3. Assess confidence levels for each intelligence category
4. Decide when to continue research or stop

INTELLIGENCE CATEGORIES:
- people: Key decision-makers, org structure, hiring patterns
- initiative: Project details, timeline, scope, status
- technology: Current stack, planned changes, vendors
- competitive: Other vendors involved, RFP/competitive dynamics
- financial: Budget signals, fiscal year, spending patterns
- market: Industry trends, regulatory factors, market position

OUTPUT FORMAT (JSON):
{
    "analysis": "Brief analysis of the current intelligence state",
    "research_paths": [
        {
            "id": "path_1",
            "topic": "Search topic or question",
            "priority": "high" | "medium" | "low",
            "category": "people" | "initiative" | "technology" | "competitive" | "financial" | "market",
            "instructions": "Specific instructions for the research sub-agent"
        }
    ],
    "confidence_assessment": {
        "people": "none" | "low" | "medium" | "high" | "sufficient",
        "initiative": "none" | "low" | "medium" | "high" | "sufficient",
        "technology": "none" | "low" | "medium" | "high" | "sufficient",
        "competitive": "none" | "low" | "medium" | "high" | "sufficient",
        "financial": "none" | "low" | "medium" | "high" | "sufficient",
        "market": "none" | "low" | "medium" | "high" | "sufficient"
    },
    "should_continue": true | false,
    "reasoning": "Why we should continue or stop"
}

GUIDELINES:
- Plan 3-5 research paths per cycle (max 5)
- Prioritize paths that fill confidence gaps
- Stop when all categories reach "sufficient" or after 5 cycles
- For follow-up questions, focus paths on the specific question
- Be specific in instructions - tell sub-agents exactly what to look for
"""


async def plan_research(
    company_name: str,
    initiative_description: str,
    industry: str | None = None,
    current_findings: dict[str, list] | None = None,
    current_confidence: dict[str, str] | None = None,
    cycle_number: int = 1,
    follow_up_question: str | None = None,
) -> dict[str, Any]:
    """
    Plan research paths for the current cycle.
    
    Args:
        company_name: Target company
        initiative_description: What we're researching
        industry: Optional industry context
        current_findings: Findings from previous cycles by category
        current_confidence: Current confidence levels by category
        cycle_number: Current cycle number (1-5)
        follow_up_question: Optional follow-up question to focus on
    
    Returns:
        Parsed planning output with research paths
    """
    # Build context message
    context_parts = [
        f"**Company:** {company_name}",
        f"**Initiative:** {initiative_description}",
    ]
    
    if industry:
        context_parts.append(f"**Industry:** {industry}")
    
    context_parts.append(f"\n**Cycle:** {cycle_number} of 5")
    
    if follow_up_question:
        context_parts.append(f"\n**Follow-up Question:** {follow_up_question}")
        context_parts.append("Focus your research paths on answering this specific question.")
    
    if current_confidence:
        context_parts.append("\n**Current Confidence Levels:**")
        for cat, level in current_confidence.items():
            context_parts.append(f"- {cat}: {level}")
    
    if current_findings:
        context_parts.append("\n**Existing Findings Summary:**")
        for cat, findings in current_findings.items():
            if findings:
                context_parts.append(f"\n*{cat.title()}:*")
                for f in findings[:3]:  # Limit to prevent context overflow
                    summary = f.get("summary", str(f))[:200]
                    context_parts.append(f"  - {summary}")
    
    user_message = "\n".join(context_parts)
    user_message += "\n\nPlan the next research cycle. Output valid JSON only."
    
    logger.info(
        "Planning research cycle",
        company=company_name,
        cycle=cycle_number,
        has_follow_up=follow_up_question is not None,
    )
    
    response = await call_claude(
        messages=[{"role": "user", "content": user_message}],
        system=PRIME_SYSTEM_PROMPT,
        max_tokens=2048,
        model="sonnet",
        temperature=0.3,  # Lower temperature for planning
    )
    
    # Parse JSON response
    try:
        # Try to extract JSON from response
        text = response["text"]
        
        # Handle markdown code blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        plan = json.loads(text.strip())
        
        # Validate structure
        if "research_paths" not in plan:
            plan["research_paths"] = []
        if "confidence_assessment" not in plan:
            plan["confidence_assessment"] = {cat.value: "none" for cat in FindingCategory}
        if "should_continue" not in plan:
            plan["should_continue"] = cycle_number < 5
        
        # Limit to 5 paths
        plan["research_paths"] = plan["research_paths"][:5]
        
        logger.info(
            "Research plan created",
            path_count=len(plan["research_paths"]),
            should_continue=plan["should_continue"],
        )
        
        return plan
        
    except json.JSONDecodeError as e:
        logger.error("Failed to parse Prime Agent response", error=str(e), text=response["text"][:500])
        
        # Return a default plan
        return {
            "analysis": "Failed to parse planning response",
            "research_paths": [
                {
                    "id": "path_1",
                    "topic": f"{company_name} {initiative_description}",
                    "priority": "high",
                    "category": "initiative",
                    "instructions": "Search for general information about this initiative",
                }
            ],
            "confidence_assessment": {cat.value: "none" for cat in FindingCategory},
            "should_continue": True,
            "reasoning": "Default plan due to parsing error",
        }


async def assess_confidence(
    findings_by_category: dict[str, list],
    previous_assessment: dict[str, str] | None = None,
) -> dict[str, str]:
    """
    Assess confidence levels based on current findings.
    
    This is a simplified version - could be enhanced with Claude.
    """
    assessment = {}
    
    for category in FindingCategory:
        cat_name = category.value
        findings = findings_by_category.get(cat_name, [])
        
        # Simple heuristic based on finding count and quality
        count = len(findings)
        
        if count == 0:
            level = "none"
        elif count == 1:
            level = "low"
        elif count <= 3:
            level = "medium"
        elif count <= 5:
            level = "high"
        else:
            level = "sufficient"
        
        # Carry forward if we had higher confidence before
        if previous_assessment:
            prev_level = previous_assessment.get(cat_name, "none")
            if _confidence_rank(prev_level) > _confidence_rank(level):
                level = prev_level
        
        assessment[cat_name] = level
    
    return assessment


def _confidence_rank(level: str) -> int:
    """Get numeric rank for confidence level."""
    ranks = {
        "none": 0,
        "low": 1,
        "medium": 2,
        "high": 3,
        "sufficient": 4,
    }
    return ranks.get(level, 0)


def should_stop_research(assessment: dict[str, str], cycle_number: int) -> bool:
    """Determine if research should stop."""
    # Stop after 5 cycles
    if cycle_number >= 5:
        return True
    
    # Stop if all categories are sufficient
    all_sufficient = all(
        level == "sufficient"
        for level in assessment.values()
    )
    if all_sufficient:
        return True
    
    # Stop if most categories are high or sufficient
    high_count = sum(
        1 for level in assessment.values()
        if level in ("high", "sufficient")
    )
    if high_count >= 5:  # 5 of 6 categories
        return True
    
    return False
