"""Multi-agent research engine."""

from .claude_client import call_claude, call_claude_with_tools, get_claude_client
from .prime import plan_research, assess_confidence, should_stop_research
from .researcher import execute_research_path, execute_research_paths_parallel
from .synthesis import synthesize_findings, generate_portfolio_recommendations
from .tools.base import Tool, ToolRegistry, create_default_registry

__all__ = [
    # Claude client
    "call_claude",
    "call_claude_with_tools",
    "get_claude_client",
    # Prime agent
    "plan_research",
    "assess_confidence",
    "should_stop_research",
    # Research sub-agents
    "execute_research_path",
    "execute_research_paths_parallel",
    # Synthesis
    "synthesize_findings",
    "generate_portfolio_recommendations",
    # Tools
    "Tool",
    "ToolRegistry",
    "create_default_registry",
]
