"""Runs API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


router = APIRouter(prefix="/runs")


class StartRunRequest(BaseModel):
    """Model for starting a run."""
    profile_id: int


class RunResponse(BaseModel):
    """Model for run response."""
    id: int
    status: str  # idle, running, paused, stopped
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    profile_id: int


# TODO: Integrate with RunWorker and service layer
@router.post("/start", response_model=RunResponse)
async def start_run(request: StartRunRequest) -> RunResponse:
    """
    Start a new application run.

    Args:
        request: Start run request with profile_id

    Returns:
        Created run
    """
    # TODO: Implement actual run start with RunWorker
    return RunResponse(
        id=1,
        status="running",
        started_at=datetime.now(),
        profile_id=request.profile_id,
    )


@router.post("/{run_id}/pause")
async def pause_run(run_id: int):
    """
    Pause a running run.

    Args:
        run_id: Run ID

    Returns:
        Success message
    """
    # TODO: Implement actual run pause
    return {"message": "Run paused"}


@router.post("/{run_id}/resume")
async def resume_run(run_id: int):
    """
    Resume a paused run.

    Args:
        run_id: Run ID

    Returns:
        Success message
    """
    # TODO: Implement actual run resume
    return {"message": "Run resumed"}


@router.post("/{run_id}/stop")
async def stop_run(run_id: int):
    """
    Stop a running or paused run.

    Args:
        run_id: Run ID

    Returns:
        Success message
    """
    # TODO: Implement actual run stop
    return {"message": "Run stopped"}


@router.post("/{run_id}/skip-job")
async def skip_current_job(run_id: int):
    """
    Skip the current job and move to the next one.

    Args:
        run_id: Run ID

    Returns:
        Success message
    """
    # TODO: Implement actual job skip
    return {"message": "Job skipped"}


@router.get("/", response_model=List[RunResponse])
async def list_runs() -> list[RunResponse]:
    """
    List all runs.

    Returns:
        List of runs
    """
    # TODO: Implement actual run listing
    return []


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(run_id: int) -> RunResponse:
    """
    Get a specific run by ID.

    Args:
        run_id: Run ID

    Returns:
        Run data
    """
    # TODO: Implement actual run retrieval
    raise HTTPException(status_code=404, detail="Run not found")
