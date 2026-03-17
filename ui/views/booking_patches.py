# -*- coding: utf-8 -*-
"""
Yalla Thailand - Tour Booking Form Patch
Adds available_trips field after the package field.
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
    "module": "tourism",
    "inheritance_operations": [
        {
            "operation": "after",
            "target": "field[name=package]",
            "content": {
                "name": "available_trips",
                "string": _("Available Trips"),
                "widget": "relation",
                "displayField": "name",
                "multiSelect": True,
                "onChange": True,
            }
        }
    ]
}
