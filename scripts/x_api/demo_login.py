"""Open a fresh Chromium with our cookies and prove login state.

Usage:
    uv run python -m scripts.x_api.demo_login
"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

from .config import load_credentials

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs"
SCREENSHOT = OUTPUT_DIR / "x_login_demo.png"


def main(keep_open: bool = True) -> None:
    creds = load_credentials()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
            locale="ja-JP",
        )
        context.add_cookies([
            {
                "name": "auth_token",
                "value": creds.auth_token,
                "domain": ".x.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "None",
            },
            {
                "name": "ct0",
                "value": creds.ct0,
                "domain": ".x.com",
                "path": "/",
                "httpOnly": False,
                "secure": True,
                "sameSite": "Lax",
            },
        ])

        page = context.new_page()
        print("Navigating to https://x.com/home ...")
        page.goto("https://x.com/home", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)

        # Logged-in indicator: SideNav_AccountSwitcher_Button or primary column
        try:
            page.wait_for_selector(
                '[data-testid="SideNav_AccountSwitcher_Button"], [data-testid="primaryColumn"]',
                timeout=15000,
            )
            print("Login indicator found.")
        except Exception:
            print("Login indicator not detected within timeout.")

        page.screenshot(path=str(SCREENSHOT), full_page=False)
        print(f"Screenshot: {SCREENSHOT}")
        print(f"Current URL: {page.url}")
        print(f"Page title:  {page.title()}")

        if keep_open:
            print("Browser kept open. Press Ctrl+C in this terminal to close.")
            try:
                page.wait_for_timeout(1000 * 60 * 30)
            except KeyboardInterrupt:
                pass

        browser.close()


if __name__ == "__main__":
    main()
