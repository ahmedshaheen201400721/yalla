"""
E2E Playwright test for Send WhatsApp Catalog Link from AvailableTrip Kanban.

Run with:
    uv run pytest /home/ahmed/Documents/system/anwer_extensions/yalla_thailand/tests/test_send_catalog_link.py -v -s
"""

import os
import django
import pytest
from playwright.sync_api import Page, expect

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

BASE_URL = "http://localhost:8000"
CHAT_URL = f"{BASE_URL}/chat/?main_tab=social&sub_tab=all&chat=fcabce2c-1dad-4a96-a9bd-0afc1a53dc54"

# Module-level DB setup — runs before Playwright event loop
from yalla_thailand.models import AvailableTrip as _Trip
_trip = _Trip.objects.filter(whatsapp_catalog_link__isnull=False).exclude(whatsapp_catalog_link="").first()
assert _trip, "No AvailableTrip with whatsapp_catalog_link in DB — add one before running this test"
TRIP_NAME = _trip.name


def test_send_catalog_link_to_whatsapp(logged_in_page: Page):
    page = logged_in_page
    page.goto(CHAT_URL)
    page.wait_for_load_state("networkidle")

    # Click "Trips" button in chat header to open the Available Trips kanban slideover
    page.get_by_role("button", name="Trips").click()
    page.wait_for_load_state("networkidle")

    # Wait for "Available Trips" kanban slideover to appear (span in slideover header)
    page.locator("span.font-semibold", has_text="Available Trips").wait_for(state="visible", timeout=10_000)

    # Select a trip card by clicking its checkbox (data-selection-checkbox)
    page.locator("[data-selection-checkbox]").first.click()
    page.wait_for_timeout(500)

    # Click "Send to WhatsApp" toolbar button
    page.get_by_role("button", name="Send to WhatsApp").click()
    page.wait_for_load_state("networkidle")

    # Assert success or informational message — must NOT be "No conversation context" error
    toast = page.locator(".toast, [role='alert']").first
    toast.wait_for(state="visible", timeout=8_000)
    toast_text = toast.inner_text()
    assert "No conversation context" not in toast_text, (
        f"conversation_id was not passed to the action — fix BaseKanban context prop: {toast_text}"
    )
    print(f"\n✓ Result: {toast_text}")
