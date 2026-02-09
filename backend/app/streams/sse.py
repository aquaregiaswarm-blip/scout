"""Server-Sent Events (SSE) manager for research sessions."""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any
import structlog

logger = structlog.get_logger()


class SSEManager:
    """
    Manages SSE connections for research sessions.
    
    Uses in-memory queues - in production, use Redis pub/sub.
    """
    
    def __init__(self):
        # session_id -> list of queues
        self._subscribers: dict[str, list[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()
    
    async def subscribe(self, session_id: str) -> asyncio.Queue:
        """Subscribe to events for a session."""
        queue: asyncio.Queue = asyncio.Queue()
        
        async with self._lock:
            if session_id not in self._subscribers:
                self._subscribers[session_id] = []
            self._subscribers[session_id].append(queue)
        
        logger.debug("SSE subscriber added", session_id=session_id)
        return queue
    
    async def unsubscribe(self, session_id: str, queue: asyncio.Queue) -> None:
        """Unsubscribe from session events."""
        async with self._lock:
            if session_id in self._subscribers:
                try:
                    self._subscribers[session_id].remove(queue)
                    if not self._subscribers[session_id]:
                        del self._subscribers[session_id]
                except ValueError:
                    pass
        
        logger.debug("SSE subscriber removed", session_id=session_id)
    
    async def publish(self, session_id: str, event: dict[str, Any]) -> None:
        """Publish an event to all subscribers for a session."""
        async with self._lock:
            subscribers = self._subscribers.get(session_id, [])
        
        if not subscribers:
            return
        
        for queue in subscribers:
            try:
                await queue.put(event)
            except Exception as e:
                logger.warning("Failed to publish to subscriber", error=str(e))
    
    async def publish_to_session(self, event: dict[str, Any]) -> None:
        """Publish event using session_id from the event."""
        session_id = event.get("session_id")
        if session_id:
            await self.publish(session_id, event)
    
    def get_subscriber_count(self, session_id: str) -> int:
        """Get number of subscribers for a session."""
        return len(self._subscribers.get(session_id, []))


# Global SSE manager instance
sse_manager = SSEManager()


async def create_event_callback(session_id: str) -> callable:
    """Create an event callback that publishes to SSE."""
    async def callback(event: dict) -> None:
        event["session_id"] = session_id
        await sse_manager.publish(session_id, event)
    return callback


def format_sse_message(event: dict) -> str:
    """Format an event as an SSE message."""
    data = json.dumps(event)
    return f"data: {data}\n\n"
