"""
ATS Adapter - Bridges v1 ATS handlers to v2 backend.

This module imports and wraps the v1 codebase modules:
- ../../resume_matching.py - ResumeMatcher
- ../../browser_automation.py - BrowserAutomator
- ../../ats_handlers/ - ATS handlers (base, greenhouse, lever)

This allows v2 to reuse all v1 automation logic without modification.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add v1 directory to Python path
v1_path = Path(__file__).parent.parent.parent


def detect_ats(job_url: str) -> Optional[str]:
    """
    Detect the ATS type from a job URL.

    Args:
        job_url: URL of the job posting

    Returns:
        ATS type ('greenhouse', 'lever', 'workday', 'ashby') or None
    """
    # Import v1 ATS handlers
    try:
        from ats_handlers.greenhouse import GreenhouseHandler
        from ats_handlers.lever import LeverHandler

        # Check Greenhouse
        if "greenhouse.io" in job_url.lower():
            return "greenhouse"

        # Check Lever
        if "jobs.lever.co" in job_url.lower():
            return "lever"

        # Note: Workday and Ashby are in v1 but can be added later
        # if "myworkdayjobs.com" in job_url.lower():
        #     return "workday"
        # if "ashbyhq.com" in job_url.lower():
        #     return "ashby"

        return None
    except ImportError as e:
        print(f"Error importing v1 ATS handlers: {e}")
        return None


async def match_resumes_to_jobs(
    jobs_csv_path: str,
    resume_base_dir: str,
) -> List[Tuple[int, str, str, str]]:
    """
    Match jobs to resumes using v1's ResumeMatcher.

    Args:
        jobs_csv_path: Path to jobs.csv
        resume_base_dir: Base directory containing numbered resume folders

    Returns:
        List of tuples: (job_id, job_url, company, resume_path)
    """
    # Import v1's ResumeMatcher
    sys.path.insert(0, str(v1_path))
    from resume_matching import ResumeMatcher

    matcher = ResumeMatcher(jobs_csv_path, resume_base_dir)

    # Get matches
    matches = matcher.match()

    # Validate matches
    from resume_matching import validate_matches
    validate_matches(matches)

    return matches


class ATSFormFiller:
    """
    Wraps v1 ATS handlers for form filling.
    """

    def __init__(self, playwright_page):
        """
        Initialize with a Playwright page.

        Args:
            playwright_page: Playwright Page object from v1's browser_automation
        """
        self.page = playwright_page

    async def fill_ats_form(
        self,
        ats_type: str,
        profile_data: Dict,
        resume_path: str,
    ) -> Dict:
        """
        Fill an ATS form using v1's handlers.

        Args:
            ats_type: ATS type ('greenhouse', 'lever', etc.)
            profile_data: User profile data
            resume_path: Path to resume file

        Returns:
            Result dictionary with status and notes
        """
        # Import v1 ATS handlers
        sys.path.insert(0, str(v1_path))
        from ats_handlers.base import ATSHandler
        from ats_handlers.greenhouse import GreenhouseHandler
        from ats_handlers.lever import LeverHandler

        # Get appropriate handler based on ATS type
        handler = self._get_handler(ats_type)

        if not handler:
            return {
                "status": "failed",
                "notes": [f"Unsupported ATS type: {ats_type}"],
            }

        # Fill the form using the v1 handler
        result = handler.fill_form(profile_data, resume_path)

        return result

    def _get_handler(self, ats_type: str) -> Optional[ATSHandler]:
        """Get the appropriate ATS handler."""
        sys.path.insert(0, str(v1_path))

        if ats_type == "greenhouse":
            from ats_handlers.greenhouse import GreenhouseHandler
            # Note: Need to adapt GreenhouseHandler to work with page object
            # For now, return a placeholder
            return None  # type: ignore
        elif ats_type == "lever":
            from ats_handlers.lever import LeverHandler
            # Note: Need to adapt LeverHandler to work with page object
            # For now, return a placeholder
            return None  # type: ignore
        else:
            return None
