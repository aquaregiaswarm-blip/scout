"""Synthesis Agent - Merges and structures findings."""

import json
import structlog
from typing import Any

from app.agents.claude_client import call_claude
from app.models.research import FindingCategory, ConfidenceLevel

logger = structlog.get_logger()

SYNTHESIS_SYSTEM_PROMPT = """You are the Synthesis Agent for Scout, an AI sales intelligence platform.

Your role is to merge research findings into structured, actionable intelligence for sales teams.

For each category, synthesize all findings into a coherent summary with key insights.

OUTPUT FORMAT (JSON):
{
    "categories": {
        "people": {
            "summary": "Paragraph summarizing key people insights",
            "key_contacts": [
                {"name": "...", "title": "...", "relevance": "..."}
            ],
            "insights": ["Key insight 1", "Key insight 2"],
            "confidence": "none" | "low" | "medium" | "high" | "sufficient"
        },
        "initiative": {
            "summary": "...",
            "timeline": "...",
            "scope": "...",
            "insights": [...],
            "confidence": "..."
        },
        "technology": {
            "summary": "...",
            "current_stack": [...],
            "planned_changes": [...],
            "insights": [...],
            "confidence": "..."
        },
        "competitive": {
            "summary": "...",
            "competitors_mentioned": [...],
            "our_position": "...",
            "insights": [...],
            "confidence": "..."
        },
        "financial": {
            "summary": "...",
            "budget_signals": [...],
            "timing": "...",
            "insights": [...],
            "confidence": "..."
        },
        "market": {
            "summary": "...",
            "trends": [...],
            "insights": [...],
            "confidence": "..."
        }
    },
    "tangential_initiatives": [
        {
            "name": "...",
            "description": "...",
            "evidence": ["..."]
        }
    ],
    "overall_assessment": "Brief overall assessment of the opportunity"
}

GUIDELINES:
- Prioritize specifics: names, dates, numbers, vendors
- Note conflicting information and indicate which seems more reliable
- Highlight actionable intelligence for sales teams
- Flag gaps that need more research
- Be concise but comprehensive
"""


async def synthesize_findings(
    company_name: str,
    initiative_description: str,
    findings_by_category: dict[str, list],
    previous_synthesis: dict | None = None,
) -> dict[str, Any]:
    """
    Synthesize findings into structured intelligence.
    
    Args:
        company_name: Target company
        initiative_description: What we're researching
        findings_by_category: Findings organized by category
        previous_synthesis: Previous synthesis to merge with
    
    Returns:
        Synthesized intelligence structure
    """
    # Build context
    context_parts = [
        f"**Company:** {company_name}",
        f"**Initiative:** {initiative_description}",
        "\n**Findings by Category:**",
    ]
    
    for category in FindingCategory:
        cat_name = category.value
        cat_findings = findings_by_category.get(cat_name, [])
        
        if cat_findings:
            context_parts.append(f"\n### {cat_name.title()}")
            for f in cat_findings:
                context_parts.append(f"- **{f.get('summary', 'No summary')}**")
                if f.get("details"):
                    context_parts.append(f"  {f['details'][:300]}")
                if f.get("source_url"):
                    context_parts.append(f"  Source: {f['source_url']}")
    
    if previous_synthesis:
        context_parts.append("\n**Previous Synthesis to Merge:**")
        context_parts.append(json.dumps(previous_synthesis, indent=2)[:2000])
    
    user_message = "\n".join(context_parts)
    user_message += "\n\nSynthesize these findings into structured intelligence. Output valid JSON only."
    
    logger.info(
        "Synthesizing findings",
        company=company_name,
        category_count=len([c for c in findings_by_category if findings_by_category[c]]),
    )
    
    response = await call_claude(
        messages=[{"role": "user", "content": user_message}],
        system=SYNTHESIS_SYSTEM_PROMPT,
        max_tokens=4096,
        model="haiku",  # Use Haiku for synthesis - faster and cheaper
        temperature=0.2,
    )
    
    # Parse response
    try:
        text = response["text"]
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        synthesis = json.loads(text.strip())
        
        logger.info("Synthesis completed", has_categories="categories" in synthesis)
        
        return synthesis
        
    except json.JSONDecodeError as e:
        logger.error("Failed to parse synthesis response", error=str(e))
        
        # Return basic structure
        return {
            "categories": {
                cat.value: {
                    "summary": "Synthesis failed - raw findings available",
                    "insights": [],
                    "confidence": "low",
                }
                for cat in FindingCategory
            },
            "overall_assessment": "Synthesis parsing failed",
            "error": str(e),
        }


async def generate_portfolio_recommendations(
    synthesis: dict,
    portfolio_items: list[dict],
) -> list[dict]:
    """
    Generate portfolio recommendations based on synthesis.
    
    Args:
        synthesis: Synthesized intelligence
        portfolio_items: Team's vendor portfolio
    
    Returns:
        List of portfolio recommendations
    """
    if not portfolio_items:
        return []
    
    # Build context
    portfolio_summary = []
    for item in portfolio_items:
        caps = ", ".join(item.get("capabilities", [])) if item.get("capabilities") else "General"
        portfolio_summary.append(f"- {item['vendor_name']} ({item.get('partnership_level', 'Partner')}): {caps}")
    
    user_message = f"""Based on this synthesized intelligence:

{json.dumps(synthesis.get('categories', {}), indent=2)[:3000]}

And this vendor portfolio:
{chr(10).join(portfolio_summary)}

Recommend which portfolio vendors are most relevant to this opportunity. Output JSON:
{{
    "recommendations": [
        {{
            "vendor": "Vendor Name",
            "capability": "Relevant capability",
            "relevance": "Why this vendor is relevant",
            "supporting_findings": ["Finding that supports this"]
        }}
    ]
}}"""

    response = await call_claude(
        messages=[{"role": "user", "content": user_message}],
        system="You recommend relevant vendor partners based on research findings. Be specific about why each vendor is relevant.",
        max_tokens=1024,
        model="haiku",
        temperature=0.3,
    )
    
    try:
        text = response["text"]
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        result = json.loads(text.strip())
        return result.get("recommendations", [])
        
    except json.JSONDecodeError:
        return []
