# -*- coding: utf-8 -*-
# Tourism Voucher Report Registration (yalla_thailand)
#
# The Report model's file template loader is hardcoded to look under
# crm/modules/<module>/templates/reports/, which can't reach extension paths.
# So we read the template from this extension's own templates dir at sync time
# and store it in Report.template_content (DB override takes precedence).
from pathlib import Path

from modules.base.models import Report
import logging

logger = logging.getLogger(__name__)

TEMPLATE_PATH = (
    Path(__file__).resolve().parent.parent
    / "templates"
    / "reports"
    / "program_voucher.html"
)

template_html = TEMPLATE_PATH.read_text(encoding="utf-8")

report, created = Report.objects.update_or_create(
    report_name="tourism.report_program_voucher",
    defaults={
        "name": "Tour Program Voucher",
        "model": "tourism.tourprogram",
        "report_type": "qweb-pdf",
        "template_name": "program_voucher.html",
        "template_content": template_html,
        "paperformat": "A4",
        "orientation": "portrait",
        "margin_top": 10,
        "margin_bottom": 10,
        "margin_left": 15,
        "margin_right": 15,
        "multi": False,
        "print_report_name": "Voucher_{{ doc.voucher_number|safe_default(doc.id) }}",
        "module": "tourism",
        "active": True,
    },
)

if created:
    print("✅ Tour Program Voucher report created")
else:
    print("✅ Tour Program Voucher report updated")
