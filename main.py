"""
Auto Applier Tool - Main entry point.

Autonomous job-application agent that reads job URLs from CSV,
matches pre-tailored resumes by folder order, fills ATS forms,
and tracks results.
"""

import os
import json
from pathlib import Path


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


def main():
    """Main entry point."""
    # Ensure we have a profile
    profile = ensure_profile()

    print("\n" + "=" * 60)
    print("Auto Applier Tool Ready")
    print("=" * 60)
    print(f"\nProfile: {profile['name']} ({profile['email']})")
    print(f"Location: {profile['location']}")

    # TODO: Implement job application loop
    print("\nComing soon: Job application automation!")
    print("This will:")
    print("  • Read job URLs from data/jobs.csv")
    print("  • Match resumes from numbered folders")
    print("  • Fill ATS forms automatically")
    print("  • Track results in data/applications.csv")


if __name__ == '__main__':
    main()
