"""Research Sub-Agent - Executes research paths with tools."""

import json
import structlog
from typing import Any

from app.agents.claude_client import call_claude_with_tools
from app.agents.tools.base import ToolRegistry, run_tool
from app.models.research import FindingCategory

logger = structlog.get_logger()

RESEARCHER_SYSTEM_PROMPT = """You are a Research Sub-Agent for Scout, an AI sales intelligence platform.

Your task is to research a specific topic and extract actionable intelligence for sales teams.

TOOLS AVAILABLE:
- web_search: Search the web for relevant pages
- web_scrape: Extract content from a specific URL
- news_search: Search for recent news articles
- sec_filings: Search SEC filings (for public companies)
- job_postings: Search job postings for hiring signals

RESEARCH GUIDELINES:
1. Start with web_search to find relevant sources
2. Use web_scrape on promising URLs to extract details
3. Look for specific, actionable intelligence:
   - Names and titles of decision-makers
   - Project timelines, budgets, scope
   - Technology vendors mentioned
   - RFP or competitive signals
   - Budget or spending indicators
4. Note your sources - URLs matter for credibility
5. Stop when you have concrete findings or exhaust relevant sources

OUTPUT FORMAT:
After your research, provide findings in this JSON format:
{
    "findings": [
        {
            "category": "people" | "initiative" | "technology" | "competitive" | "financial" | "market",
            "summary": "One-sentence summary of the finding",
            "details": "Detailed explanation with specifics",
            "source_url": "URL where this was found",
            "confidence": 0.0-1.0
        }
    ],
    "tangential_signals": [
        "Brief note about related initiatives or opportunities discovered"
    ],
    "search_exhausted": true | false
}

Be specific. Names, dates, and numbers are more valuable than vague statements.
"""


async def execute_research_path(
    topic: str,
    instructions: str,
    target_category: str,
    company_name: str,
    tool_registry: ToolRegistry,
    max_tool_calls: int = 10,
) -> dict[str, Any]:
    """
    Execute a single research path.
    
    Args:
        topic: The research topic/question
        instructions: Specific instructions from Prime Agent
        target_category: Primary category to focus on
        company_name: Company being researched
        tool_registry: Registry of available tools
        max_tool_calls: Maximum number of tool calls
    
    Returns:
        Research results with findings
    """
    # Build initial message
    user_message = f"""Research Task:
**Topic:** {topic}
**Company:** {company_name}
**Target Category:** {target_category}

**Instructions:**
{instructions}

Use the available tools to research this topic. When you have gathered enough information, provide your findings in the JSON format specified."""

    # Tool executor function
    async def execute_tool(name: str, input_data: dict) -> str:
        result = await run_tool(tool_registry, name, input_data)
        if "error" in result:
            return f"Error: {result['error']}"
        return json.dumps(result.get("result", {}), indent=2)
    
    logger.info(
        "Starting research path",
        topic=topic,
        category=target_category,
        company=company_name,
    )
    
    # Execute research loop
    response = await call_claude_with_tools(
        messages=[{"role": "user", "content": user_message}],
        system=RESEARCHER_SYSTEM_PROMPT,
        tools=tool_registry.to_anthropic_tools(),
        tool_executor=execute_tool,
        max_turns=max_tool_calls,
        model="sonnet",
    )
    
    # Parse findings from response
    try:
        text = response["text"]
        
        # Extract JSON from response
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        result = json.loads(text.strip())
        
        # Ensure findings have required fields
        findings = []
        for f in result.get("findings", []):
            findings.append({
                "category": f.get("category", target_category),
                "summary": f.get("summary", ""),
                "details": f.get("details", ""),
                "source_url": f.get("source_url"),
                "confidence": float(f.get("confidence", 0.5)),
            })
        
        logger.info(
            "Research path completed",
            topic=topic,
            finding_count=len(findings),
            tool_calls=len(response.get("tool_results", [])),
        )
        
        return {
            "findings": findings,
            "tangential_signals": result.get("tangential_signals", []),
            "search_exhausted": result.get("search_exhausted", False),
            "tool_results": response.get("tool_results", []),
            "turns": response.get("turns", 0),
            "usage": response.get("usage", {}),
        }
        
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(
            "Failed to parse research response",
            error=str(e),
            topic=topic,
        )
        
        # Return empty findings on parse error
        return {
            "findings": [],
            "tangential_signals": [],
            "search_exhausted": True,
            "error": str(e),
            "raw_response": response.get("text", "")[:500],
        }


async def execute_research_paths_parallel(
    paths: list[dict],
    company_name: str,
    tool_registry: ToolRegistry,
    max_parallel: int = 5,
) -> list[dict[str, Any]]:
    """
    Execute multiple research paths in parallel.
    
    Args:
        paths: List of research path definitions
        company_name: Company being researched
        tool_registry: Registry of available tools
        max_parallel: Maximum concurrent paths
    
    Returns:
        List of results for each path
    """
    import asyncio
    
    # Limit parallelism
    paths = paths[:max_parallel]
    
    async def run_path(path: dict) -> dict:
        try:
            result = await execute_research_path(
                topic=path["topic"],
                instructions=path.get("instructions", ""),
                target_category=path.get("category", "initiative"),
                company_name=company_name,
                tool_registry=tool_registry,
            )
            return {
                "path_id": path.get("id", "unknown"),
                "topic": path["topic"],
                "category": path.get("category", "initiative"),
                "status": "completed",
                **result,
            }
        except Exception as e:
            logger.error(
                "Research path failed",
                path_id=path.get("id"),
                error=str(e),
            )
            return {
                "path_id": path.get("id", "unknown"),
                "topic": path["topic"],
                "category": path.get("category", "initiative"),
                "status": "error",
                "error": str(e),
                "findings": [],
            }
    
    logger.info("Executing research paths", path_count=len(paths))
    
    results = await asyncio.gather(*[run_path(p) for p in paths])
    
    # Count successful paths
    success_count = sum(1 for r in results if r["status"] == "completed")
    total_findings = sum(len(r.get("findings", [])) for r in results)
    
    logger.info(
        "Research paths completed",
        success_count=success_count,
        total_count=len(paths),
        total_findings=total_findings,
    )
    
    return results
