#!/usr/bin/env python3
"""
Keep a Streamlit Community Cloud app awake.

Community Cloud hibernates any app with no traffic for 12 hours. A plain
HTTP GET won't wake it: it returns a 200 with a static HTML shell, and the
Python process never starts. This script drives a real headless browser
(Playwright) to load the page, run the JS, open the WebSocket, and click the
"Yes, get this app back up!" button if the app is asleep.

Run it on a schedule (see .github/workflows/keepalive.yml). It exits non-zero
on failure so a GitHub Actions run surfaces problems instead of silently
going green.
"""

import os
import sys

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

APP_URL = os.environ.get("APP_URL", "https://ragforge-app.streamlit.app/")
WAKE_BUTTON_LABEL = "Yes, get this app back up!"

# Navigation timeout and how long to allow the container to spin back up (ms).
NAV_TIMEOUT_MS = 120_000
WAKE_SETTLE_MS = 90_000


def main() -> int:
    print(f"Visiting {APP_URL}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            )
        )

        try:
            page.goto(
                APP_URL,
                wait_until="domcontentloaded",
                timeout=NAV_TIMEOUT_MS,
            )
        except PlaywrightTimeoutError:
            print("ERROR: navigation timed out", file=sys.stderr)
            browser.close()
            return 1

        # Let Streamlit render either the sleep page or the live app.
        page.wait_for_timeout(5_000)

        wake_button = page.get_by_role("button", name=WAKE_BUTTON_LABEL)

        if wake_button.count() > 0:
            print("App was asleep -- clicking the wake button.")
            wake_button.first.click()
            try:
                # Confirmation: the wake button goes away once the app loads.
                page.wait_for_selector(
                    f'button:has-text("{WAKE_BUTTON_LABEL}")',
                    state="detached",
                    timeout=WAKE_SETTLE_MS,
                )
                print("App is back up.")
            except PlaywrightTimeoutError:
                print(
                    "WARNING: wake button still present after waiting; "
                    "app may still be starting.",
                    file=sys.stderr,
                )
        else:
            print("App was already awake.")

        browser.close()

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
