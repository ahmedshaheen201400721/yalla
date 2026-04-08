# -*- coding: utf-8 -*-
"""
Yalla Thailand - Tour Program Patches
Adds pickup_time, hotel, room_num, and actual pricing fields to program views.
"""
from django.utils.translation import gettext as _


# =============================================================================
# BATCH 1: Add fields to inline programs list in Booking Form
# =============================================================================
tourprogram_booking_form_yalla_batch = {
    "key": "tourprogram_booking_form_yalla_batch",
    "name": "Tour Booking Form - Program Yalla Fields",
    "model": "tourism.tourbooking",
    "view_type": "form",
    "priority": 25,
    "inherit_mode": "extension",
    "inherit_id": "tourism_booking_form",
    "module": "tourism",
    "inheritance_operations": [
        # Voucher number column (hidden by default, toggleable)
        {
            "operation": "before",
            "target": "field[name=programs.name]",
            "content": {"name": "programs.voucher_number", "widget": "text", "string": _("Voucher #"), "onChange": True, "visible": False, "readonly": True},
        },
        # Pickup/Hotel/Room fields
        {
            "operation": "after",
            "target": "field[name=programs.notes]",
            "content": {"name": "programs.pickup_time", "widget": "datetime", "string": _("Pickup Time"), "onChange": True, "visible": True},
        },
        {
            "operation": "after",
            "target": "field[name=programs.pickup_time]",
            "content": {"name": "programs.hotel", "widget": "relation", "string": _("Hotel"), "onChange": True, "visible": True, "displayField": "name"},
        },
        {
            "operation": "after",
            "target": "field[name=programs.hotel]",
            "content": {"name": "programs.room_num", "widget": "text", "string": _("Room #"), "onChange": True, "visible": True},
        },
        # Actual pricing fields for agents
        {
            "operation": "after",
            "target": "field[name=programs.room_num]",
            "content": {"name": "programs.actual_adult_price", "widget": "number", "string": _("Actual Adult Price"), "onChange": True, "visible": True},
        },
        {
            "operation": "after",
            "target": "field[name=programs.actual_adult_price]",
            "content": {"name": "programs.actual_child_price", "widget": "number", "string": _("Actual Child Price"), "onChange": True, "visible": True},
        },
    ]
}


# =============================================================================
# BATCH 2: Add fields to standalone Program Form
# =============================================================================
tourprogram_form_yalla_batch = {
    "key": "tourprogram_form_yalla_batch",
    "name": "Tour Program Form - Yalla Fields",
    "model": "tourism.tourprogram",
    "view_type": "form",
    "priority": 30,
    "inherit_mode": "extension",
    "inherit_id": "tourism_program_form",
    "module": "tourism",
    "inheritance_operations": [
        # Print Voucher header action
        {
            "operation": "append",
            "target": "header.actions",
            "content": {
                "name": "action_print_voucher",
                "type": "server",
                "as": "button",
                "string": _("Print Voucher"),
                "icon": "Printer",
                "confirm_required": False,
            },
        },
        # Voucher number field (readonly, auto-generated)
        {
            "operation": "before",
            "target": "field[name=booking]",
            "content": {"name": "voucher_number", "widget": "text", "string": _("Voucher #"), "readonly": True},
        },
        # Pickup/Hotel/Room fields after title
        {
            "operation": "after",
            "target": "field[name=day_number]",
            "content": {"name": "pickup_time", "string": _("Pickup Time"), "widget": "datetime"},
        },
        {
            "operation": "after",
            "target": "field[name=pickup_time]",
            "content": {
                "name": "hotel",
                "string": _("Hotel"),
                "widget": "relation",
                "displayField": "name",
                "domain": {"filters": {"operator": "and", "filters": [{"field": "is_hotel", "operator": "eq", "value": True}]}},
                'context': {
                    'default_fields': {
                        'is_hotel': True
                    }
                }
            },
        },
        {
            "operation": "after",
            "target": "field[name=hotel]",
            "content": {"name": "room_num", "string": _("Room #"), "widget": "text"},
        },
        # Catalog snapshot fields (readonly) after child_price
        {
            "operation": "after",
            "target": "field[name=child_price]",
            "content": {"name": "actual_adult_price", "string": _("Catalog Adult Price"), "widget": "number", "readonly": True},
        },
        {
            "operation": "after",
            "target": "field[name=actual_adult_price]",
            "content": {"name": "actual_child_price", "string": _("Catalog Child Price"), "widget": "number", "readonly": True},
        },
        # Relabel price_per_person to "Adult Price" and wire onChange for floor validation
        {
            "operation": "modify",
            "target": "field[name=price_per_person]",
            "content": {"string": _("Adult Price"), "onChange": True},
        },
        # Wire onChange on child_price for floor validation
        {
            "operation": "modify",
            "target": "field[name=child_price]",
            "content": {"onChange": True},
        },
        # Restrict supplier/cost/markup fields to managers (agents edit Adult/Child Price only)
        {
            "operation": "modify",
            "target": "field[name=total_price]",
            "content": {"edit_groups": ["tourism.managers"]},
        },
        {
            "operation": "modify",
            "target": "field[name=markup]",
            "content": {"edit_groups": ["tourism.managers"]},
        },
        {
            "operation": "modify",
            "target": "field[name=supplier]",
            "content": {"edit_groups": ["tourism.managers"]},
        },
        {
            "operation": "modify",
            "target": "field[name=cost_price]",
            "content": {"edit_groups": ["tourism.managers"]},
        },
        {
            "operation": "modify",
            "target": "field[name=child_cost]",
            "content": {"edit_groups": ["tourism.managers"]},
        },
    ]
}
