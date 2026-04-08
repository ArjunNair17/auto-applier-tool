"""
Base ATS handler class.

Defines the interface for all ATS-specific handlers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from playwright.sync_api import Page


class ATSHandler(ABC):
    """Abstract base class for ATS-specific form handlers."""

    def __init__(self, page: Page):
        """
        Initialize the handler with a Playwright page.

        Args:
            page: Playwright Page object
        """
        self.page = page

    @classmethod
    @abstractmethod
    def detect(cls, page: Page) -> bool:
        """
        Detect if the current page is using this ATS.

        Args:
            page: Playwright Page object

        Returns:
            True if this ATS is detected, False otherwise
        """
        pass

    @abstractmethod
    def fill_form(self, profile_data: Dict[str, str], resume_path: str) -> Dict[str, str]:
        """
        Fill out the application form.

        Args:
            profile_data: Dictionary with user profile data
            resume_path: Path to the resume PDF file

        Returns:
            Dictionary with status and any notes/errors
        """
        pass

    def extract_required_fields(self) -> List[Dict[str, str]]:
        """
        Extract required fields from the form.

        Returns:
            List of required fields with labels and selectors
        """
        return []

    def is_app_form_present(self) -> bool:
        """
        Check if an application form is present on the page.

        Returns:
            True if form is found, False otherwise
        """
        return self.page.query_selector('form') is not None

    def fill_input_by_label(self, label_text: str, value: str) -> bool:
        """
        Fill an input field by its associated label.

        Args:
            label_text: Text of the label to find
            value: Value to fill

        Returns:
            True if field was found and filled, False otherwise
        """
        # Try to find label containing the text
        label = self.page.query_selector(f'text={label_text}')
        if not label:
            return False

        # Get the associated input (next sibling or by for attribute)
        input_elem = None

        # Try by for attribute
        for_id = label.get_attribute('for')
        if for_id:
            input_elem = self.page.query_selector(f'#{for_id}')
            if not input_elem:
                input_elem = self.page.query_selector(f'input[name="{for_id}"]')

        # Try next sibling
        if not input_elem:
            input_elem = label.query_selector('xpath=following-sibling::input[1]')

        if not input_elem:
            return False

        # Fill the field
        input_type = input_elem.get_attribute('type') or 'text'
        if input_type == 'file':
            input_elem.set_input_files(value)
        else:
            input_elem.fill(value)

        return True

    def fill_input_by_selector(self, selector: str, value: str, timeout: int = 5000) -> bool:
        """
        Fill an input field by CSS selector.

        Args:
            selector: CSS selector for the input element
            value: Value to fill
            timeout: Maximum wait time in milliseconds

        Returns:
            True if field was found and filled, False otherwise
        """
        try:
            elem = self.page.wait_for_selector(selector, timeout=timeout)
            if elem:
                input_type = elem.get_attribute('type') or 'text'
                if input_type == 'file':
                    elem.set_input_files(value)
                else:
                    elem.fill(value)
                return True
        except Exception:
            pass

        return False

    def click_button_by_text(self, text: str, timeout: int = 5000) -> bool:
        """
        Click a button by its text content.

        Args:
            text: Text to search for in the button
            timeout: Maximum wait time in milliseconds

        Returns:
            True if button was found and clicked, False otherwise
        """
        try:
            btn = self.page.wait_for_selector(f'button:has-text("{text}")', timeout=timeout)
            if btn:
                btn.click()
                return True
        except Exception:
            pass

        return False
