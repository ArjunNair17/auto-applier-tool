"""
Resume matching module for pairing jobs with tailored resumes.

Reads jobs.csv, scans numbered folders for PDF resumes, and matches them
by folder index order.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Optional
import pandas as pd


class ResumeMatcher:
    """Matches jobs to resumes based on numbered folder order."""

    def __init__(self, jobs_csv_path: str, resume_base_dir: str):
        """
        Initialize the matcher.

        Args:
            jobs_csv_path: Path to jobs.csv with columns: job_url, company_name
            resume_base_dir: Base directory containing numbered resume folders
        """
        self.jobs_csv_path = jobs_csv_path
        self.resume_base_dir = Path(resume_base_dir)

    def load_jobs(self) -> pd.DataFrame:
        """
        Load jobs from CSV file.

        Returns:
            DataFrame with job_url and company_name columns

        Raises:
            FileNotFoundError: If CSV doesn't exist
            ValueError: If CSV is missing required columns
        """
        if not os.path.exists(self.jobs_csv_path):
            raise FileNotFoundError(f"Jobs CSV not found: {self.jobs_csv_path}")

        df = pd.read_csv(self.jobs_csv_path)

        required_cols = ['job_url', 'company_name']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"CSV missing required columns: {missing_cols}")

        return df[required_cols]

    def find_resume_folders(self) -> List[Path]:
        """
        Find all numbered resume folders sorted by index.

        Looks for folders matching pattern: XX_Name/ where XX is a number

        Returns:
            List of folder paths sorted by numeric prefix

        Raises:
            FileNotFoundError: If resume_base_dir doesn't exist
        """
        if not self.resume_base_dir.exists():
            raise FileNotFoundError(f"Resume directory not found: {self.resume_base_dir}")

        folders = []
        pattern = re.compile(r'^(\d{1,3})_.+$')

        for item in self.resume_base_dir.iterdir():
            if item.is_dir():
                match = pattern.match(item.name)
                if match:
                    idx = int(match.group(1))
                    folders.append((idx, item))

        # Sort by numeric index
        folders.sort(key=lambda x: x[0])

        return [folder for _, folder in folders]

    def find_resume_pdf(self, folder: Path) -> Optional[Path]:
        """
        Find a PDF resume in the given folder.

        Args:
            folder: Folder path to search

        Returns:
            Path to PDF file if found, None otherwise

        Raises:
            ValueError: If multiple PDFs found (ambiguous)
        """
        pdfs = list(folder.glob('*.pdf'))

        if len(pdfs) == 0:
            return None
        elif len(pdfs) == 1:
            return pdfs[0]
        else:
            raise ValueError(f"Multiple PDFs found in {folder}: {pdfs}")

    def match(self) -> List[Tuple[int, str, str, str]]:
        """
        Match jobs to resumes by folder index order.

        Returns:
            List of tuples: (job_id, job_url, company_name, resume_path)

        Raises:
            ValueError: If job count doesn't match resume folder count
            ValueError: If any resume folder doesn't contain exactly one PDF
        """
        jobs_df = self.load_jobs()
        resume_folders = self.find_resume_folders()

        job_count = len(jobs_df)
        resume_count = len(resume_folders)

        if job_count != resume_count:
            raise ValueError(
                f"Job count ({job_count}) doesn't match resume folder count ({resume_count}). "
                f"Ensure you have one numbered folder per job."
            )

        matches = []
        for idx, (_, row) in enumerate(jobs_df.iterrows()):
            folder = resume_folders[idx]
            resume_path = self.find_resume_pdf(folder)

            if resume_path is None:
                raise ValueError(f"No PDF found in {folder}")

            matches.append((
                idx + 1,  # job_id (1-indexed)
                row['job_url'],
                row['company_name'],
                str(resume_path)
            ))

        return matches


def validate_matches(matches: List[Tuple[int, str, str, str]]) -> None:
    """
    Validate that all resume paths exist.

    Args:
        matches: List of (job_id, job_url, company_name, resume_path)

    Raises:
        FileNotFoundError: If any resume file doesn't exist
    """
    for job_id, _, _, resume_path in matches:
        if not os.path.exists(resume_path):
            raise FileNotFoundError(f"Resume file not found for job {job_id}: {resume_path}")
