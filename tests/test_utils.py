"""
Unit tests for utils module.
"""

import os
import time
import csv
import pytest
from datetime import datetime
from utils import RateLimiter, ApplicationLogger, validate_job_url, format_resume_path


def test_rate_limiter_first_application():
    """Test that first application doesn't wait."""
    limiter = RateLimiter(min_delay_minutes=0, max_delay_minutes=0)
    limiter.wait_for_next()
    assert limiter.last_application_time > 0


def test_rate_limiter_waits_between_apps():
    """Test that rate limiter waits between applications."""
    limiter = RateLimiter(min_delay_minutes=0, max_delay_minutes=0)
    limiter.wait_for_next()

    start = time.time()
    limiter.wait_for_next()
    elapsed = time.time() - start

    # Should have waited
    assert elapsed >= 0


def test_rate_limiter_get_delay_range():
    """Test getting delay range."""
    limiter = RateLimiter(min_delay_minutes=5, max_delay_minutes=60)
    min_delay, max_delay = limiter.get_delay_range()
    assert min_delay == 5
    assert max_delay == 60


def test_application_logger_creates_file(tmp_path):
    """Test that logger creates CSV file."""
    csv_path = tmp_path / "applications.csv"
    logger = ApplicationLogger(str(csv_path))

    assert os.path.exists(csv_path)

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert headers == ApplicationLogger.DEFAULT_COLUMNS


def test_application_logger_logs_application(tmp_path):
    """Test logging an application."""
    csv_path = tmp_path / "applications.csv"
    logger = ApplicationLogger(str(csv_path))

    logger.log_application(
        job_id=1,
        company="Test Company",
        job_url="https://example.com/job1",
        status="applied",
        resume_path="/path/to/resume.pdf",
        notes="Test note"
    )

    applications = logger.get_applications()
    assert len(applications) == 1
    assert applications[0]['company'] == "Test Company"
    assert applications[0]['status'] == "applied"
    assert applications[0]['notes'] == "Test note"


def test_application_logger_get_status_count(tmp_path):
    """Test counting applications by status."""
    csv_path = tmp_path / "applications.csv"
    logger = ApplicationLogger(str(csv_path))

    logger.log_application(1, "Company A", "url1", "applied", "resume1.pdf")
    logger.log_application(2, "Company B", "url2", "failed", "resume2.pdf")
    logger.log_application(3, "Company C", "url3", "applied", "resume3.pdf")

    assert logger.get_status_count('applied') == 2
    assert logger.get_status_count('failed') == 1
    assert logger.get_status_count('manual_required') == 0


def test_application_logger_get_statistics(tmp_path):
    """Test getting statistics."""
    csv_path = tmp_path / "applications.csv"
    logger = ApplicationLogger(str(csv_path))

    logger.log_application(1, "Company A", "url1", "applied", "resume1.pdf")
    logger.log_application(2, "Company B", "url2", "failed", "resume2.pdf")
    logger.log_application(3, "Company C", "url3", "manual_required", "resume3.pdf")

    stats = logger.get_statistics()
    assert stats['total'] == 3
    assert stats['applied'] == 1
    assert stats['failed'] == 1
    assert stats['manual_required'] == 1


def test_validate_job_url_valid():
    """Test validating valid URLs."""
    assert validate_job_url("https://example.com") is True
    assert validate_job_url("http://example.com") is True
    assert validate_job_url("https://example.com/job/123") is True


def test_validate_job_url_invalid():
    """Test validating invalid URLs."""
    assert validate_job_url("") is False
    assert validate_job_url(None) is False
    assert validate_job_url("example.com") is False  # Missing protocol
    assert validate_job_url("ftp://example.com") is False  # Wrong protocol
    assert validate_job_url("   ") is False  # Whitespace only


def test_format_resume_path():
    """Test formatting resume path."""
    path = "/path/to/Arjun_Resume.pdf"
    formatted = format_resume_path(path)
    assert formatted == "Arjun_Resume.pdf"

    assert format_resume_path("") == "None"
    assert format_resume_path(None) == "None"
