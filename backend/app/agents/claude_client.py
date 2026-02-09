"""Claude client via Vertex AI."""

import structlog
from anthropic import AnthropicVertex
from typing import Any

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# Model mapping
CLAUDE_MODELS = {
    "sonnet": "claude-sonnet-4@20250514",
    "haiku": "claude-haiku-4@20250514",  # For synthesis/presentation
}


def get_claude_client() -> AnthropicVertex:
    """Get Anthropic client configured for Vertex AI."""
    return AnthropicVertex(
        region=settings.vertex_ai_region,
        project_id=settings.gcp_project_id,
    )


async def call_claude(
    messages: list[dict],
    system: str | None = None,
    tools: list[dict] | None = None,
    max_tokens: int = 4096,
    model: str = "sonnet",
    temperature: float = 0.7,
) -> dict[str, Any]:
    """
    Call Claude via Vertex AI.
    
    Args:
        messages: Conversation messages
        system: System prompt
        tools: Tool definitions for tool use
        max_tokens: Max tokens to generate
        model: Model name ("sonnet" or "haiku")
        temperature: Sampling temperature
    
    Returns:
        {
            "content": list of content blocks,
            "stop_reason": str,
            "usage": {"input_tokens": int, "output_tokens": int},
            "tool_calls": list of tool use blocks (if any),
        }
    """
    client = get_claude_client()
    model_id = CLAUDE_MODELS.get(model, CLAUDE_MODELS["sonnet"])
    
    logger.info(
        "Calling Claude",
        model=model_id,
        message_count=len(messages),
        has_tools=tools is not None,
    )
    
    kwargs = {
        "model": model_id,
        "max_tokens": max_tokens,
        "messages": messages,
        "temperature": temperature,
    }
    
    if system:
        kwargs["system"] = system
    
    if tools:
        kwargs["tools"] = tools
    
    response = client.messages.create(**kwargs)
    
    # Extract tool calls if any
    tool_calls = []
    text_content = []
    
    for block in response.content:
        if block.type == "tool_use":
            tool_calls.append({
                "id": block.id,
                "name": block.name,
                "input": block.input,
            })
        elif block.type == "text":
            text_content.append(block.text)
    
    logger.info(
        "Claude response received",
        stop_reason=response.stop_reason,
        tool_call_count=len(tool_calls),
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )
    
    return {
        "content": response.content,
        "text": "\n".join(text_content),
        "stop_reason": response.stop_reason,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
        "tool_calls": tool_calls,
    }


async def call_claude_with_tools(
    messages: list[dict],
    system: str,
    tools: list[dict],
    tool_executor: callable,
    max_turns: int = 10,
    model: str = "sonnet",
) -> dict[str, Any]:
    """
    Call Claude in a tool-use loop until completion.
    
    Args:
        messages: Initial conversation messages
        system: System prompt
        tools: Tool definitions
        tool_executor: Async function to execute tools (name, input) -> result
        max_turns: Maximum agentic turns
        model: Model to use
    
    Returns:
        Final response with all tool results accumulated
    """
    current_messages = list(messages)
    all_tool_results = []
    turns = 0
    
    while turns < max_turns:
        turns += 1
        
        response = await call_claude(
            messages=current_messages,
            system=system,
            tools=tools,
            model=model,
        )
        
        # Check if we need to handle tool calls
        if response["stop_reason"] != "tool_use" or not response["tool_calls"]:
            # Done - no more tool calls
            response["tool_results"] = all_tool_results
            response["turns"] = turns
            return response
        
        # Execute tool calls
        tool_use_content = response["content"]
        tool_results = []
        
        for tool_call in response["tool_calls"]:
            logger.info(
                "Executing tool",
                tool=tool_call["name"],
                turn=turns,
            )
            
            result = await tool_executor(tool_call["name"], tool_call["input"])
            
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call["id"],
                "content": str(result) if not isinstance(result, str) else result,
            })
            
            all_tool_results.append({
                "tool": tool_call["name"],
                "input": tool_call["input"],
                "result": result,
            })
        
        # Add assistant message and tool results to conversation
        current_messages.append({
            "role": "assistant",
            "content": tool_use_content,
        })
        current_messages.append({
            "role": "user",
            "content": tool_results,
        })
    
    logger.warning("Max turns reached in tool loop", max_turns=max_turns)
    response["tool_results"] = all_tool_results
    response["turns"] = turns
    return response
