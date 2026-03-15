# -*- coding: utf-8 -*-
"""
Yalla Thailand - Tour Booking Form Patch
Adds available_trip field after the package field.
"""
from django.utils.translation import gettext as _


tourism_booking_form_yalla_patch = {
    "key": "tourism_booking_form_yalla_patch",
    "name": "Tour Booking Form - Yalla Available Trip Patch",
    "model": "tourism.tourbooking",
    "view_type": "form",
    "priority": 20,
    "inherit_mode": "extension",
    "inherit_id": "tourism_booking_form",
    "module": "yalla_thailand",
    "inheritance_operations": [
        {
            "operation": "insert",
            "target": "sheet.sections.0.groups.0.fields",
            "index": 2,
            "content": [
                {
                    "name": "available_trip",
                    "string": _("Available Trip"),
                    "widget": "relation",
                    "displayField": "name",
                    "multiSelect": False,
                    "onChange": True,
                }
            ]
        }
    ]
}
