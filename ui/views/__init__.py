# -*- coding: utf-8 -*-
"""Yalla Thailand UI views package"""

from .available_trip_views import (
    available_trip_list_view,
    available_trip_form_view,
    available_trip_search_view,
    available_trip_kanban_view,
)

from .account_move_patches import (
    invoice_form_view_yalla_patch,
    vendor_bill_form_view_yalla_patch,
    journal_entry_form_view_yalla_patch,
    credit_note_form_view_yalla_patch,
    vendor_refund_form_view_yalla_patch,
    invoice_form_client_paid_supplier_patch,
)

from .partner_form_patch import (
    partner_form_yalla_settle_patch,
)

from .sales_order_patches import (
    salesorder_form_view_yalla_patch,
    sales_quote_form_view_yalla_patch,
)

from .purchase_order_patches import (
    purchase_order_form_view_yalla_patch,
    purchase_ready_order_form_view_yalla_patch,
)

from .booking_patches import (
    tourism_booking_form_yalla_patch,
)

__all__ = [
    # AvailableTrip standalone views
    'available_trip_list_view',
    'available_trip_form_view',
    'available_trip_search_view',
    'available_trip_kanban_view',

    # Account move patches
    'invoice_form_view_yalla_patch',
    'vendor_bill_form_view_yalla_patch',
    'journal_entry_form_view_yalla_patch',
    'credit_note_form_view_yalla_patch',
    'vendor_refund_form_view_yalla_patch',

    # Sales order patches
    'salesorder_form_view_yalla_patch',
    'sales_quote_form_view_yalla_patch',

    # Purchase order patches
    'purchase_order_form_view_yalla_patch',
    'purchase_ready_order_form_view_yalla_patch',

    # Client paid supplier patch
    'invoice_form_client_paid_supplier_patch',

    # Partner settle patch
    'partner_form_yalla_settle_patch',

    # Tour Booking - available trip patch
    'tourism_booking_form_yalla_patch',
]
