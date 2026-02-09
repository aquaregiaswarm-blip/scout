"""Base tool interface and registry for research sub-agents."""

from abc import ABC, abstractmethod
from typing import Any
import asyncio
import structlog

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class Tool(ABC):
    """Base class for all research tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description for the AI."""
        pass
    
    @property
    @abstractmethod
    def schema(self) -> dict:
        """Anthropic tool use JSON schema."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> dict:
        """Execute the tool and return structured results."""
        pass
    
    def to_anthropic_tool(self) -> dict:
        """Convert to Anthropic tool definition format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.schema,
        }


class ToolRegistry:
    """Registry of available tools for research sub-agents."""
    
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        logger.debug("Tool registered", tool=tool.name)
    
    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())
    
    def to_anthropic_tools(self) -> list[dict]:
        """Get all tools in Anthropic format."""
        return [tool.to_anthropic_tool() for tool in self._tools.values()]


async def run_tool(
    registry: ToolRegistry,
    tool_name: str,
    tool_input: dict[str, Any],
    timeout: float | None = None,
) -> dict:
    """
    Execute a tool with timeout and error handling.
    
    Returns a dict with either:
    - {"result": <tool_output>} on success
    - {"error": <message>, "tool": <name>} on failure
    """
    tool = registry.get(tool_name)
    
    if tool is None:
        logger.warning("Unknown tool requested", tool=tool_name)
        return {"error": f"Unknown tool: {tool_name}", "tool": tool_name}
    
    timeout = timeout or settings.tool_timeout_seconds
    
    try:
        logger.info("Executing tool", tool=tool_name, input_keys=list(tool_input.keys()))
        
        result = await asyncio.wait_for(
            tool.execute(**tool_input),
            timeout=timeout,
        )
        
        logger.info("Tool completed", tool=tool_name, result_keys=list(result.keys()) if isinstance(result, dict) else "non-dict")
        return {"result": result}
        
    except asyncio.TimeoutError:
        logger.warning("Tool timed out", tool=tool_name, timeout=timeout)
        return {"error": f"Tool timed out after {timeout}s", "tool": tool_name}
        
    except Exception as e:
        logger.error("Tool execution failed", tool=tool_name, error=str(e))
        return {"error": str(e), "tool": tool_name}


def create_default_registry() -> ToolRegistry:
    """Create a registry with all default tools."""
    from app.agents.tools.web_search import WebSearchTool
    from app.agents.tools.web_scrape import WebScrapeTool
    from app.agents.tools.sec_filings import SECFilingsTool
    from app.agents.tools.news_search import NewsSearchTool
    from app.agents.tools.job_postings import JobPostingsTool
    
    registry = ToolRegistry()
    registry.register(WebSearchTool())
    registry.register(WebScrapeTool())
    registry.register(SECFilingsTool())
    registry.register(NewsSearchTool())
    registry.register(JobPostingsTool())
    
    return registry
