"""Job management business logic services."""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.models import Job, JobBatch
from ..db.repo import JobRepository
from ..db.schema import JobCreate, JobResponse


class JobService:
    """Service for job management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.job_repo = JobRepository(session)

    async def import_from_csv(self, csv_path: str, profile_id: int) -> JobBatch:
        """Import jobs from a CSV file."""
        # TODO: Implement actual CSV parsing
        # TODO: Use v1's resume_matching.py to scan folder
        # TODO: Match CSV rows to folder indices
        raise NotImplementedError("CSV import not yet implemented")

    async def import_from_folder(self, folder_path: str, profile_id: int) -> JobBatch:
        """Import jobs by scanning folder for numbered subdirectories."""
        # TODO: Implement actual folder scanning
        # TODO: Use v1's resume_matching.py to scan folder
        # TODO: Match folder order to jobs
        raise NotImplementedError("Folder import not yet implemented")

    async def list_jobs(self) -> List[JobResponse]:
        """List all jobs."""
        jobs = await self.job_repo.get_all()
        return [
            JobResponse(
                id=job.id,
                job_url=job.job_url,
                company=job.company,
                resume_path=job.resume_path,
                ats_type=job.ats_type,
                status=job.status,
            )
            for job in jobs
        ]

    async def get_job(self, job_id: int) -> JobResponse:
        """Get a specific job."""
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        return JobResponse(
            id=job.id,
            job_url=job.job_url,
            company=job.company,
            resume_path=job.resume_path,
            ats_type=job.ats_type,
            status=job.status,
        )

    async def delete_job(self, job_id: int) -> None:
        """Delete a job."""
        await self.job_repo.delete_by_id(job_id)

    async def clear_all_jobs(self) -> None:
        """Clear all jobs."""
        jobs = await self.job_repo.get_all()
        for job in jobs:
            await self.job_repo.delete(job)
