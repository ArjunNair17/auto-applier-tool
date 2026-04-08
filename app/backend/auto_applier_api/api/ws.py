"""WebSocket API endpoint for real-time events."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict


router = APIRouter()


# WebSocket event types
EVENT_TYPES = [
    "log",
    "screenshot",
    "intervention.required",
    "job.started",
    "job.finished",
    "run.started",
    "run.finished",
]


class WSMessage(BaseModel):
    """WebSocket message model."""
    event_type: str
    data: Dict


# TODO: Implement actual WebSocket connection manager
# This should manage connections and broadcast events
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time events.

    Events:
        - log: Log messages during runs
        - screenshot: Browser screenshots for preview
        - intervention.required: Manual intervention needed
        - job.started: Job processing started
        - job.finished: Job completed
        - run.started: Run session started
        - run.finished: Run session completed
    """
    # TODO: Implement actual WebSocket connection manager
    # Should accept connection, manage in a list, broadcast to all clients
    try:
        await websocket.accept()
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Handle any commands from frontend if needed
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")


# TODO: Create functions to broadcast events to all connected clients
async def broadcast_log(message: str, level: str = "info"):
    """Broadcast a log message to all clients."""
    # TODO: Implement actual broadcast
    pass


async def broadcast_screenshot(base64_image: str):
    """Broadcast a browser screenshot to all clients."""
    # TODO: Implement actual broadcast
    pass


async def broadcast_intervention(reason: str, screenshot_base64: Optional[str] = None):
    """Broadcast an intervention required event."""
    # TODO: Implement actual broadcast
    pass


async def broadcast_job_started(job_id: int, company: str):
    """Broadcast job started event."""
    # TODO: Implement actual broadcast
    pass


async def broadcast_job_finished(job_id: int, status: str):
    """Broadcast job finished event."""
    # TODO: Implement actual broadcast
    pass
