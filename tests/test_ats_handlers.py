"""
Unit tests for ATS handlers.
"""

import pytest
from playwright.sync_api import Page
from ats_handlers.base import ATSHandler
from ats_handlers.greenhouse import GreenhouseHandler
from ats_handlers.lever import LeverHandler


class MockPage:
    """Mock Page object for testing."""

    def __init__(self, url: str = ""):
        self.url = url
        self._selectors_found = {}

    def query_selector(self, selector: str):
        """Return True if selector is in found set."""
        return self._selectors_found.get(selector, False)

    def set_selectors(self, selectors: dict):
        """Set which selectors should be found."""
        self._selectors_found = selectors


def test_greenhouse_detect_by_url():
    """Test Greenhouse detection via URL."""
    page = MockPage(url="https://boards.greenhouse.io/example/jobs/12345")
    assert GreenhouseHandler.detect(page) is True

    page.url = "https://example.com/jobs"
    assert GreenhouseHandler.detect(page) is False


def test_greenhouse_detect_by_elements():
    """Test Greenhouse detection via form elements."""
    page = MockPage(url="https://example.com/apply")
    page.set_selectors({
        '#job_application_name': True,
        'input[type="file"]': True,
    })
    assert GreenhouseHandler.detect(page) is True

    page.set_selectors({})
    assert GreenhouseHandler.detect(page) is False


def test_lever_detect_by_url():
    """Test Lever detection via URL."""
    page = MockPage(url="https://jobs.lever.co/example/67890")
    assert LeverHandler.detect(page) is True

    page.url = "https://example.com/jobs"
    assert LeverHandler.detect(page) is False


def test_lever_detect_by_elements():
    """Test Lever detection via form elements."""
    page = MockPage(url="https://example.com/apply")
    page.set_selectors({
        'input[data-qa="email"]': True,
    })
    assert LeverHandler.detect(page) is True

    page.set_selectors({
        '.application-form': True,
    })
    assert LeverHandler.detect(page) is True

    page.set_selectors({})
    assert LeverHandler.detect(page) is False


def test_ats_handler_is_abstract():
    """Test that ATSHandler cannot be instantiated directly."""
    page = MockPage()
    with pytest.raises(TypeError):
        ATSHandler(page)
