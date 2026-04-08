"""
Utility functions and classes.

Includes rate limiting, application logging, and helper functions.
"""

import os
import time
import random
import csv
from datetime import datetime
from typing import List, Dict, Optional


class RateLimiter:
    """Rate limiter for controlling application frequency."""

    def __init__(self, min_delay_minutes: int = 12, max_delay_minutes: int = 60):
        """
        Initialize the rate limiter.

        Args:
            min_delay_minutes: Minimum delay between applications (default 12 min = 5 apps/hour)
            max_delay_minutes: Maximum delay between applications (default 60 min = 1 app/hour)
        """
        self.min_delay = min_delay_minutes * 60  # Convert to seconds
        self.max_delay = max_delay_minutes * 60  # Convert to seconds
        self.last_application_time = 0

    def wait_for_next(self) -> None:
        """Wait until it's time for the next application."""
        if self.last_application_time == 0:
            # First application, no wait needed
            self.last_application_time = time.time()
            return

        elapsed = time.time() - self.last_application_time

        if elapsed < self.min_delay:
            wait_time = random.uniform(self.min_delay, self.max_delay)
            remaining = wait_time - elapsed

            if remaining > 0:
                print(f"\n⏳ Rate limiting: Waiting {int(remaining / 60)} minutes before next application...")
                time.sleep(remaining)

        self.last_application_time = time.time()

    def get_delay_range(self) -> tuple:
        """
        Get the current delay range in minutes.

        Returns:
            Tuple of (min_delay_minutes, max_delay_minutes)
        """
        return (self.min_delay / 60, self.max_delay / 60)


class ApplicationLogger:
    """Logger for tracking application results."""

    DEFAULT_COLUMNS = [
        'job_id',
        'company',
        'job_url',
        'status',
        'resume_path',
        'timestamp',
        'notes',
    ]

    def __init__(self, csv_path: str = 'data/applications.csv'):
        """
        Initialize the logger.

        Args:
            csv_path: Path to the CSV file for logging
        """
        self.csv_path = csv_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensure the CSV file exists with headers."""
        if not os.path.exists(self.csv_path):
            # Create directory if needed
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)

            # Create file with headers
            with open(self.csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.DEFAULT_COLUMNS)

    def log_application(
        self,
        job_id: int,
        company: str,
        job_url: str,
        status: str,
        resume_path: str,
        notes: str = '',
    ) -> None:
        """
        Log an application result.

        Args:
            job_id: Job identifier (row number)
            company: Company name
            job_url: Job posting URL
            status: Application status (applied, failed, manual_required, etc.)
            resume_path: Path to the resume used
            notes: Additional notes or errors
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                job_id,
                company,
                job_url,
                status,
                resume_path,
                timestamp,
                notes,
            ])

        print(f"✓ Logged: {company} - {status}")

    def get_applications(self) -> List[Dict[str, str]]:
        """
        Get all logged applications.

        Returns:
            List of dictionaries with application data
        """
        if not os.path.exists(self.csv_path):
            return []

        applications = []
        with open(self.csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                applications.append(row)

        return applications

    def get_status_count(self, status: str) -> int:
        """
        Get the count of applications with a specific status.

        Args:
            status: Status to count

        Returns:
            Number of applications with the given status
        """
        applications = self.get_applications()
        return sum(1 for app in applications if app.get('status') == status)

    def get_statistics(self) -> Dict[str, int]:
        """
        Get application statistics.

        Returns:
            Dictionary with counts for each status
        """
        applications = self.get_applications()
        stats = {
            'total': len(applications),
            'applied': 0,
            'failed': 0,
            'manual_required': 0,
            'skipped': 0,
            'needs_email_verification': 0,
        }

        for app in applications:
            status = app.get('status', '')
            if status in stats:
                stats[status] += 1

        return stats

    def print_statistics(self) -> None:
        """Print application statistics to console."""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("Application Statistics")
        print("=" * 60)
        print(f"Total applications: {stats['total']}")
        print(f"✓ Applied: {stats['applied']}")
        print(f"✗ Failed: {stats['failed']}")
        print(f"⚠️  Manual required: {stats['manual_required']}")
        print(f"⏭️  Skipped: {stats['skipped']}")
        print(f"📧 Email verification: {stats['needs_email_verification']}")
        print("=" * 60 + "\n")


def validate_job_url(url: str) -> bool:
    """
    Validate that a URL is properly formatted.

    Args:
        url: URL to validate

    Returns:
        True if URL is valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()
    if not url:
        return False

    return url.startswith(('http://', 'https://'))


def format_resume_path(resume_path: str) -> str:
    """
    Format a resume path for display or logging.

    Args:
        resume_path: Path to resume file

    Returns:
        Formatted resume path (just filename)
    """
    return os.path.basename(resume_path) if resume_path else 'None'
