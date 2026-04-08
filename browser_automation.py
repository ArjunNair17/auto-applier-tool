"""
Browser automation module using Playwright.

Provides Playwright wrapper for browser automation with support for
manual intervention, CAPTCHA detection, and various form helpers.
"""

import time
from typing import Optional, List
from playwright.sync_api import Page, Browser, BrowserContext


class BrowserAutomator:
    """Playwright browser automation with manual intervention support."""

    def __init__(self, headless: bool = False):
        """
        Initialize the browser automator.

        Args:
            headless: If False, run in headed mode (default for manual intervention)
        """
        self.headless = headless
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    def start(self):
        """Start the browser and create a new page."""
        from playwright.sync_api import sync_playwright

        playwright = sync_playwright().start()

        # Launch browser (headed by default for manual intervention)
        self._browser = playwright.chromium.launch(
            headless=self.headless,
            slow_mo=50  # Slight delay for debugging/observation
        )

        # Create a new context with realistic user agent
        self._context = self._browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800},
        )

        # Create a new page
        self._page = self._context.new_page()

        # Set default timeout
        self._page.set_default_timeout(30000)  # 30 seconds

        return self._page

    def stop(self):
        """Stop the browser and cleanup resources."""
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()

    @property
    def page(self) -> Page:
        """Get the current page."""
        if self._page is None:
            raise RuntimeError("Browser not started. Call start() first.")
        return self._page

    def goto(self, url: str) -> None:
        """
        Navigate to a URL.

        Args:
            url: URL to navigate to
        """
        self.page.goto(url, wait_until='networkidle')

    def pause_for_manual_intervention(self, reason: str) -> None:
        """
        Pause execution and wait for user to complete manual action.

        This keeps the browser open and waits for the user to press Enter.

        Args:
            reason: Description of why manual intervention is needed
        """
        print("\n" + "=" * 70)
        print("⚠️  MANUAL INTERVENTION NEEDED")
        print("=" * 70)
        print(f"\nReason: {reason}")
        print("\nThe browser is open. Please complete the required action manually.")
        print("\nCommon actions:")
        print("  • Solve CAPTCHA")
        print("  • Fill in free-text questions")
        print("  • Complete email verification")
        print("  • Upload additional documents")
        print("\nOnce complete, return to this terminal and press Enter to continue...")
        print("=" * 70 + "\n")

        input("⏸️  Press Enter when done: ")

        print("✓ Resuming automation...\n")

    def detect_captcha(self) -> bool:
        """
        Detect if CAPTCHA is present on the page.

        Looks for common CAPTCHA elements:
        - reCAPTCHA
        - hCaptcha
        - Cloudflare

        Returns:
            True if CAPTCHA detected, False otherwise
        """
        captcha_selectors = [
            '[class*="recaptcha"]',
            '[id*="recaptcha"]',
            '[class*="hcaptcha"]',
            '[id*="hcaptcha"]',
            '.cf-browser-verification',
            'iframe[src*="recaptcha"]',
            'iframe[src*="hcaptcha"]',
            '.captcha-container',
        ]

        for selector in captcha_selectors:
            try:
                element = self.page.query_selector(selector)
                if element:
                    # Check if element is visible
                    if element.is_visible():
                        print(f"⚠️  CAPTCHA detected: {selector}")
                        return True
            except Exception:
                pass

        return False

    def detect_free_text_questions(self) -> List[str]:
        """
        Detect free-text questions (textarea elements) on the page.

        Returns:
            List of selectors for detected textareas
        """
        textarea_selectors = self.page.query_selector_all('textarea')

        questions = []
        for idx, textarea in enumerate(textarea_selectors, 1):
            try:
                if textarea.is_visible():
                    # Try to find associated label
                    label = textarea.query_selector('xpath=preceding-sibling::label')
                    label_text = label.inner_text().strip() if label else f"Question {idx}"

                    questions.append(f"  {idx}. {label_text}")
            except Exception:
                pass

        if questions:
            print(f"\n⚠️  Detected {len(questions)} free-text question(s):")
            for q in questions:
                print(q)

        return questions

    def detect_email_verification(self) -> bool:
        """
        Detect if email verification is required.

        Looks for common email verification indicators.

        Returns:
            True if email verification detected, False otherwise
        """
        verification_keywords = [
            'verify email',
            'confirm email',
            'check your email',
            'verification code',
            'email confirmation',
        ]

        page_text = self.page.inner_text('body').lower()

        for keyword in verification_keywords:
            if keyword in page_text:
                print(f"⚠️  Email verification detected (keyword: '{keyword}')")
                return True

        return False

    def wait_for_navigation(self, timeout: int = 30000) -> None:
        """
        Wait for page navigation to complete.

        Args:
            timeout: Maximum wait time in milliseconds
        """
        self.page.wait_for_load_state('networkidle', timeout=timeout)

    def take_screenshot(self, filename: str) -> None:
        """
        Take a screenshot of the current page.

        Args:
            filename: Path to save the screenshot
        """
        self.page.screenshot(path=filename, full_page=True)
        print(f"📸 Screenshot saved to: {filename}")

    def get_page_info(self) -> dict:
        """
        Get information about the current page.

        Returns:
            Dictionary with page title and URL
        """
        return {
            'title': self.page.title(),
            'url': self.page.url,
        }
