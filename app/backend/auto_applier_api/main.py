"""FastAPI backend for Auto-Applier v2."""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .settings import Settings, get_data_dir
from .api import profiles, jobs, runs, applications, settings


# Initialize settings
settings = Settings()

# Get data directory
get_data_dir()

# Create FastAPI app
app = FastAPI(
    title="Auto-Applier API",
    description="Backend for Auto-Applier v2 Desktop Application",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(profiles.router, prefix="/api/profiles")
app.include_router(jobs.router, prefix="/api/jobs")
app.include_router(runs.router, prefix="/api/runs")
app.include_router(applications.router, prefix="/api/applications")
app.include_router(settings.router, prefix="/api/settings")

# WebSocket manager
class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("Auto-Applier API starting up...")
    print(f"Data directory: {get_data_dir()}")
    print(f"API will be available at: http://{settings.api_host}:{settings.api_port}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("Auto-Applier API shutting down...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Auto-Applier API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time events."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Handle any commands from frontend if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


def get_server_url() -> str:
    """Get the server URL for Tauri to connect to."""
    return f"http://{settings.api_host}:{settings.api_port}"


async def main():
    """Main entry point for running the server."""
    import uvicorn

    # Find an available port if not specified
    port = settings.api_port
    if port == 0:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            port = s.getsockname()[1]

    print(f"\n{'='*60}")
    print("Auto-Applier FastAPI Server")
    print(f"Server running on http://{settings.api_host}:{port}")
    print(f"Press Ctrl+C to stop")
    print(f"{'='*60}\n")

    config = uvicorn.Config(
        app=app,
        host=settings.api_host,
        port=port,
        log_level="info",
    )

    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
