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
                "string": _("Available Tours"),
                "widget": "relation",
                "displayField": "name",
                "multiSelect": True,
                "onChange": True,
            }
        },
        {
            "operation": "modify",
            "target": "field[name=supplier]",
            "content": {
                "allowed_groups": ["yalla_thailand.hotels", "yalla_thailand.transport"]
            }
        },
        {
            "operation": "modify",
            "target": "field[name=start_date]",
            "content": {
                "edit_groups": ["tourism.managers", "yalla_thailand.hotels"]
            }
        },
        {
            "operation": "modify",
            "target": "field[name=end_date]",
            "content": {
                "edit_groups": ["tourism.managers", "yalla_thailand.hotels"]
            }
        },
        {
            "operation": "modify",
            "target": "field[name=package]",
            "content": {
                "edit_groups": ["tourism.managers", "yalla_thailand.hotels"]
            }
        },
        # Remove base buttons that yalla reorganizes (re-appended below in the target order).
        {"operation": "remove", "target": "action[name=action_create_quotation]"},
        {"operation": "remove", "target": "action[name=action_create_purchase_order]"},
        {"operation": "remove", "target": "action[name=action_print_customer_itinerary]"},
        {"operation": "remove", "target": "action[name=action_confirm]"},
        {"operation": "remove", "target": "action[name=action_send_customer_itinerary]"},
        {"operation": "remove", "target": "action[name=action_cancel]"},
        # Final header order after appends: Start, Done, Set to Draft, Refund, Accountant,
        # Print (dropdown), Cancel, Send, Send Link, Confirm.
        {
            "operation": "append",
            "target": "header.actions",
            "content": {
                "string": _("Accountant"),
                "icon": "FileStack",
                "name": "action_create_so_and_pos",
                "type": "server",
                "as": "button",
                "variant": "primary",
                "confirm_required": False,
                "invisible": {
                    "or": [
                        {"field": "sale_order", "operator": "is_not_null"},
                        {"field": "state", "operator": "ne", "value": "confirmed"},
                    ]
                },
            }
        },
        {
            "operation": "append",
            "target": "header.actions",
            "content": {
                "string": _("Print"),
                "icon": "Printer",
                "name": "action_print_customer_itinerary",
                "type": "server",
                "as": "dropdown",
                "confirm_required": False,
                "invisible": {"field": "state", "operator": "in", "value": ["cancelled", "refunded"]},
            }
        },
        {
            "operation": "append",
            "target": "header.actions",
            "content": {
                "string": _("Cancel"),
                "icon": "X",
                "name": "action_cancel",
                "type": "server",
                "as": "button",
                "confirm_required": True,
                "allowed_groups": ["tourism.managers"],
                "invisible": {"field": "state", "operator": "not_in", "value": ["confirmed", "paid", "partially_paid", "ongoing"]},
            }
        },
        {
            "operation": "append",
            "target": "header.actions",
            "content": {
                "string": _("Send"),
                "icon": "Send",
                "name": "action_send_customer_itinerary",
                "type": "server",
                "as": "button",
                "confirm_required": False,
                "invisible": {"field": "state", "operator": "in", "value": ["cancelled", "refunded"]},
            }
        },
        {
            "operation": "append",
            "target": "header.actions",
            "content": {
                "string": _("Send Link"),
                "icon": "CreditCard",
                "name": "send_omise_payment_link",
                "type": "server",
                "as": "button",
                "variant": "primary",
                "confirm_required": False,
            }
        },
        {
            "operation": "append",
            "target": "header.actions",
            "content": {
                "string": _("Confirm"),
                "icon": "Check",
                "name": "action_confirm",
                "type": "server",
                "as": "button",
                "confirm_required": False,
                "invisible": {"field": "state", "operator": "in", "value": ["confirmed", "paid", "partially_paid", "ongoing", "done", "cancelled", "refunded"]},
            }
        },
    ]
}
