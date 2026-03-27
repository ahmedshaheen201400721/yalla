import pytest
from playwright.sync_api import sync_playwright, Page, Browser

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASSWORD = "Admin123$%"


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=False, slow_mo=500)
        yield b
        b.close()


@pytest.fixture(scope="session")
def logged_in_page(browser: Browser):
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"{BASE_URL}/login/")
    page.fill('[name="email"]', ADMIN_EMAIL)
    page.fill('[name="password"]', ADMIN_PASSWORD)
    page.click('[type="submit"]')
    page.wait_for_url(f"{BASE_URL}/**", timeout=10_000)
    yield page
    context.close()
