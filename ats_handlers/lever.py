"""
Lever ATS handler.

Handles form filling for Lever-based job applications.
"""

from typing import Dict
from playwright.sync_api import Page
from .base import ATSHandler


class LeverHandler(ATSHandler):
    """Handler for Lever ATS job applications."""

    # Common Lever selectors
    SELECTORS = {
        'name': [
            'input[name="name"]',
            'input[data-qa="name"]',
            '#name',
        ],
        'email': [
            'input[name="email"]',
            'input[data-qa="email"]',
            '#email',
        ],
        'phone': [
            'input[name="phone"]',
            'input[data-qa="phone"]',
            '#phone',
        ],
        'resume': [
            'input[type="file"]',
            'input[name="resume"]',
            'input[data-qa="resume"]',
        ],
        'submit': [
            'button[type="submit"]',
            'button:has-text("Submit Application")',
            'button:has-text("Submit")',
        ],
    }

    @classmethod
    def detect(cls, page: Page) -> bool:
        """
        Detect if the current page is using Lever ATS.

        Args:
            page: Playwright Page object

        Returns:
            True if Lever is detected, False otherwise
        """
        url = page.url.lower()

        # Check URL for Lever indicators
        if 'jobs.lever.co' in url:
            return True

        # Check for common Lever form elements
        if page.query_selector('input[data-qa="email"]'):
            return True

        # Lever often uses specific structure
        if page.query_selector('.application-form'):
            return True

        return False

    def fill_form(self, profile_data: Dict[str, str], resume_path: str) -> Dict[str, str]:
        """
        Fill out the Lever application form.

        Args:
            profile_data: Dictionary with user profile data
            resume_path: Path to the resume PDF file

        Returns:
            Dictionary with status and any notes/errors
        """
        result = {
            'status': 'success',
            'notes': []
        }

        try:
            # Wait for form to be present
            if not self.is_app_form_present():
                return {
                    'status': 'failed',
                    'notes': ['Application form not found on page']
                }

            # Fill basic fields
            if profile_data.get('name'):
                self._fill_field('name', profile_data['name'])

            if profile_data.get('email'):
                self._fill_field('email', profile_data['email'])

            if profile_data.get('phone'):
                self._fill_field('phone', profile_data['phone'])

            # Upload resume
            if resume_path:
                success = self._upload_resume(resume_path)
                if not success:
                    result['status'] = 'manual_required'
                    result['notes'].append('Resume upload failed - manual intervention required')

            # Fill optional fields if present
            if profile_data.get('linkedin'):
                self._fill_field('linkedin', profile_data['linkedin'])

            if profile_data.get('github'):
                self._fill_field('github', profile_data['github'])

            if profile_data.get('portfolio'):
                self._fill_field('portfolio', profile_data['portfolio'])

            if profile_data.get('location'):
                self._fill_field('location', profile_data['location'])

            # Fill work authorization if present
            if profile_data.get('work_authorization'):
                self._fill_field('work_authorization', profile_data['work_authorization'])

            result['notes'].append('Form filled - ready for submission')

        except Exception as e:
            result['status'] = 'failed'
            result['notes'].append(f'Error filling form: {str(e)}')

        return result

    def _fill_field(self, field_name: str, value: str) -> bool:
        """
        Fill a field using multiple selector fallbacks.

        Args:
            field_name: Name of the field to fill
            value: Value to fill

        Returns:
            True if field was filled successfully, False otherwise
        """
        selectors = self.SELECTORS.get(field_name, [])
        for selector in selectors:
            try:
                elem = self.page.wait_for_selector(selector, timeout=3000)
                if elem:
                    input_type = elem.get_attribute('type') or 'text'
                    if input_type == 'file':
                        elem.set_input_files(value)
                    else:
                        elem.fill(value)
                    return True
            except Exception:
                continue

        return False

    def _upload_resume(self, resume_path: str) -> bool:
        """
        Upload the resume file.

        Args:
            resume_path: Path to the resume PDF file

        Returns:
            True if upload successful, False otherwise
        """
        selectors = self.SELECTORS.get('resume', [])
        for selector in selectors:
            try:
                elem = self.page.wait_for_selector(selector, timeout=3000)
                if elem:
                    elem.set_input_files(resume_path)
                    return True
            except Exception:
                continue

        return False

    def submit_form(self) -> bool:
        """
        Submit the application form.

        Returns:
            True if submission successful, False otherwise
        """
        selectors = self.SELECTORS.get('submit', [])
        for selector in selectors:
            try:
                elem = self.page.wait_for_selector(selector, timeout=5000)
                if elem:
                    elem.click()
                    return True
            except Exception:
                continue

        return False
