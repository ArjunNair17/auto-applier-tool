"""
Auto Applier Tool - Main entry point.

Autonomous job-application agent that reads job URLs from CSV,
matches pre-tailored resumes by folder order, fills ATS forms,
and tracks results.
"""

import os
import json
import sys
from pathlib import Path
from typing import Optional

from resume_matching import ResumeMatcher, validate_matches
from browser_automation import BrowserAutomator
from ats_handlers.greenhouse import GreenhouseHandler
from ats_handlers.lever import LeverHandler
from utils import RateLimiter, ApplicationLogger, validate_job_url


PROFILE_FIELDS = [
    ('name', 'Full name'),
    ('email', 'Email address'),
    ('phone', 'Phone number'),
    ('linkedin', 'LinkedIn profile URL (optional)'),
    ('github', 'GitHub profile URL (optional)'),
    ('portfolio', 'Portfolio website URL (optional)'),
    ('location', 'Location (e.g., "San Francisco, CA")'),
    ('work_authorization', 'Work authorization status (e.g., "US Citizen", "H1B", "Green Card")'),
]


def get_profile_path() -> str:
    """Get the path to the profile configuration file."""
    return os.path.join('config', 'profile.json')


def profile_exists() -> bool:
    """Check if a profile configuration file exists."""
    return os.path.exists(get_profile_path())


def load_profile() -> dict:
    """
    Load user profile from JSON file.

    Returns:
        Dictionary with profile data

    Raises:
        FileNotFoundError: If profile file doesn't exist
        json.JSONDecodeError: If profile file is invalid JSON
    """
    with open(get_profile_path(), 'r') as f:
        return json.load(f)


def save_profile(profile: dict) -> None:
    """
    Save user profile to JSON file.

    Args:
        profile: Dictionary with profile data
    """
    profile_path = get_profile_path()

    # Ensure config directory exists
    os.makedirs(os.path.dirname(profile_path), exist_ok=True)

    with open(profile_path, 'w') as f:
        json.dump(profile, f, indent=2)


def collect_profile_interactive() -> dict:
    """
    Collect user profile data through interactive CLI prompts.

    Returns:
        Dictionary with profile data
    """
    print("\n" + "=" * 60)
    print("Auto Applier Tool - Profile Setup")
    print("=" * 60)
    print("\nPlease provide your profile information for job applications.")
    print("This will be saved to config/profile.json\n")

    profile = {}

    for field, label in PROFILE_FIELDS:
        while True:
            value = input(f"{label}: ").strip()

            # Required fields
            if field in ['name', 'email', 'phone', 'location', 'work_authorization']:
                if not value:
                    print(f"  ⚠️  {label} is required. Please try again.")
                    continue

            # Optional fields - can be empty
            if not value and field not in ['name', 'email', 'phone', 'location', 'work_authorization']:
                value = None

            profile[field] = value
            break

    print("\n" + "-" * 60)
    print("Profile Summary:")
    print("-" * 60)
    for field, label in PROFILE_FIELDS:
        value = profile.get(field, '(not provided)')
        print(f"  {label}: {value}")
    print("-" * 60 + "\n")

    confirm = input("Save this profile? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Profile setup cancelled.")
        exit(1)

    return profile


def ensure_profile() -> dict:
    """
    Ensure user profile exists, creating it if necessary.

    Returns:
        Dictionary with profile data
    """
    if profile_exists():
        print("✓ Found existing profile at config/profile.json")
        return load_profile()

    print("No profile found. Let's set one up.")
    profile = collect_profile_interactive()
    save_profile(profile)

    print(f"\n✓ Profile saved to {get_profile_path()}")
    return profile


def detect_ats_handler(page):
    """
    Detect which ATS handler to use for the current page.

    Args:
        page: Playwright Page object

    Returns:
        ATSHandler instance or None if not supported
    """
    if GreenhouseHandler.detect(page):
        return GreenhouseHandler(page)
    elif LeverHandler.detect(page):
        return LeverHandler(page)
    else:
        return None


def apply_to_job(
    browser: BrowserAutomator,
    job_id: int,
    job_url: str,
    company: str,
    resume_path: str,
    profile: dict,
    logger: ApplicationLogger,
) -> str:
    """
    Apply to a single job.

    Args:
        browser: BrowserAutomator instance
        job_id: Job identifier
        job_url: Job posting URL
        company: Company name
        resume_path: Path to resume
        profile: User profile data
        logger: ApplicationLogger instance

    Returns:
        Application status (applied, failed, manual_required, etc.)
    """
    print(f"\n{'=' * 60}")
    print(f"Job {job_id}: {company}")
    print(f"URL: {job_url}")
    print('=' * 60)

    try:
        # Validate URL
        if not validate_job_url(job_url):
            logger.log_application(
                job_id=job_id,
                company=company,
                job_url=job_url,
                status='failed',
                resume_path=resume_path,
                notes='Invalid URL format'
            )
            return 'failed'

        # Navigate to job posting
        print(f"\n🌐 Navigating to {job_url}...")
        browser.goto(job_url)

        # Detect ATS
        print("🔍 Detecting ATS...")
        handler = detect_ats_handler(browser.page)

        if not handler:
            print("⚠️  Unsupported ATS detected")
            logger.log_application(
                job_id=job_id,
                company=company,
                job_url=job_url,
                status='manual_required',
                resume_path=resume_path,
                notes='Unsupported ATS - manual intervention required'
            )
            return 'manual_required'

        print(f"✓ ATS detected: {handler.__class__.__name__}")

        # Check for CAPTCHA
        if browser.detect_captcha():
            print("\n⚠️  CAPTCHA detected!")
            browser.pause_for_manual_intervention("CAPTCHA detected - please solve manually")
            logger.log_application(
                job_id=job_id,
                company=company,
                job_url=job_url,
                status='manual_required',
                resume_path=resume_path,
                notes='CAPTCHA required manual intervention'
            )
            return 'manual_required'

        # Check for email verification
        if browser.detect_email_verification():
            print("\n⚠️  Email verification required!")
            browser.pause_for_manual_intervention("Email verification - please verify email manually")
            logger.log_application(
                job_id=job_id,
                company=company,
                job_url=job_url,
                status='needs_email_verification',
                resume_path=resume_path,
                notes='Email verification required'
            )
            return 'needs_email_verification'

        # Check for free-text questions
        free_text = browser.detect_free_text_questions()
        if free_text:
            print("\n⚠️  Free-text questions detected!")
            browser.pause_for_manual_intervention(f"{len(free_text)} free-text question(s) - please answer manually")

        # Fill the form
        print("\n📝 Filling out application form...")
        result = handler.fill_form(profile, resume_path)

        # Handle form filling result
        if result['status'] == 'failed':
            print(f"✗ Failed to fill form: {result['notes']}")
            logger.log_application(
                job_id=job_id,
                company=company,
                job_url=job_url,
                status='failed',
                resume_path=resume_path,
                notes='; '.join(result['notes'])
            )
            return 'failed'

        elif result['status'] == 'manual_required':
            print("\n⚠️  Manual intervention required")
            browser.pause_for_manual_intervention('; '.join(result['notes']))
            logger.log_application(
                job_id=job_id,
                company=company,
                job_url=job_url,
                status='manual_required',
                resume_path=resume_path,
                notes='; '.join(result['notes'])
            )
            return 'manual_required'

        print("\n✓ Form filled successfully")

        # Pause for final review and submission
        print("\n" + "=" * 60)
        print("Review the form before submission.")
        print("Press Enter to submit, or 's' to skip this application.")
        print("=" * 60)

        choice = input("Submit application? [Enter/skip]: ").strip().lower()

        if choice == 's' or choice == 'skip':
            logger.log_application(
                job_id=job_id,
                company=company,
                job_url=job_url,
                status='skipped',
                resume_path=resume_path,
                notes='Skipped by user'
            )
            return 'skipped'

        # Submit the form
        print("\n📤 Submitting application...")
        if handler.submit_form():
            print("✓ Application submitted!")
            logger.log_application(
                job_id=job_id,
                company=company,
                job_url=job_url,
                status='applied',
                resume_path=resume_path,
                notes='Successfully submitted'
            )
            return 'applied'
        else:
            print("✗ Failed to submit form")
            logger.log_application(
                job_id=job_id,
                company=company,
                job_url=job_url,
                status='manual_required',
                resume_path=resume_path,
                notes='Submit button not found - manual intervention required'
            )
            return 'manual_required'

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        logger.log_application(
            job_id=job_id,
            company=company,
            job_url=job_url,
            status='failed',
            resume_path=resume_path,
            notes=f'Exception: {str(e)}'
        )
        return 'failed'


def run_applications():
    """Main application loop."""
    # Ensure we have a profile
    profile = ensure_profile()

    # Initialize logger and rate limiter
    logger = ApplicationLogger()
    rate_limiter = RateLimiter(min_delay_minutes=12, max_delay_minutes=60)

    # Load and match jobs to resumes
    jobs_csv = 'data/jobs.csv'
    resume_base = '.'  # Current directory

    print(f"\n📂 Loading jobs from {jobs_csv}...")
    print(f"📁 Matching resumes from {resume_base}...")

    try:
        matcher = ResumeMatcher(jobs_csv, resume_base)
        matches = matcher.match()
        validate_matches(matches)

        print(f"✓ Found {len(matches)} job(s) to apply to\n")

    except Exception as e:
        print(f"\n✗ Error loading jobs: {str(e)}")
        print("Please ensure:")
        print("  • data/jobs.csv exists with job_url and company_name columns")
        print("  • Numbered resume folders exist (01_*, 02_*, etc.)")
        print("  • Each folder contains exactly one PDF resume")
        sys.exit(1)

    # Initialize browser
    print("\n🚀 Starting browser...")
    browser = BrowserAutomator(headless=False)  # Headed for manual intervention
    browser.start()

    try:
        # Process each job
        for job_id, job_url, company, resume_path in matches:
            status = apply_to_job(
                browser=browser,
                job_id=job_id,
                job_url=job_url,
                company=company,
                resume_path=resume_path,
                profile=profile,
                logger=logger,
            )

            # Wait before next application (rate limiting)
            if job_id < len(matches):
                rate_limiter.wait_for_next()

    finally:
        # Print statistics
        logger.print_statistics()

        # Stop browser
        print("\n🛑 Closing browser...")
        browser.stop()
        print("✓ Done!")


def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("Auto Applier Tool")
    print("=" * 60)
    print("\nAutonomous job application automation")

    run_applications()



if __name__ == '__main__':
    main()
