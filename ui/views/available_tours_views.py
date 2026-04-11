# -*- coding: utf-8 -*-
"""
Yalla Thailand - AvailableTrip standalone UI views
(list, form, search)
"""
from django.utils.translation import gettext as _


# =============================================================================
# LIST VIEW
# =============================================================================
available_trip_list_view = {
    "key": "yalla_available_trip_list",
    "name": "Available Tours",
    "model": "yalla_thailand.availabletrip",
    "view_type": "list",
    "module": "yalla_thailand",
    "menu_item": "yalla_thailand_available_tours",
    "priority": 10,
    "body": {
        "tree": {
            "fields": [
                {"name": "name",           "widget": "text",     "string": _("Name"),         "width": 200},
                {"name": "destination",    "widget": "select",   "string": _("Destination"),  "width": 130},
                {"name": "supplier",       "widget": "relation", "string": _("Supplier"),     "displayField": "name", "width": 150},
                {"name": "activity_type",  "widget": "select",   "string": _("Act. Type"),    "width": 110},
                {"name": "duration",       "widget": "select",   "string": _("Duration"),     "width": 100},
                {"name": "time",           "widget": "select",   "string": _("Time"),         "width": 110},
                {"name": "quality",        "widget": "select",   "string": _("Quality"),      "width": 100},
                {"name": "price_range",    "widget": "select",   "string": _("Price Range"),  "width": 120},
                {"name": "sell_prc_adult", "widget": "number",   "string": _("Sell Ad."),     "width": 100},
                {"name": "net_prc_adult",  "widget": "number",   "string": _("Net Ad."),      "width": 100},
                {"name": "sell_prc_child", "widget": "number",   "string": _("Sell PRC Ch."), "width": 100},
                {"name": "net_prc_child",  "widget": "number",   "string": _("Net PRC Ch."),  "width": 100},
                {"name": "min_markup",     "widget": "number",   "string": _("Min. Markup"),  "width": 100},
            ]
        }
    }
}


# =============================================================================
# FORM VIEW
# =============================================================================
available_trip_form_view = {
    "key": "yalla_available_trip_form",
    "name": "Available Trip Form",
    "model": "yalla_thailand.availabletrip",
    "view_type": "form",
    "module": "yalla_thailand",
    "menu_item": "yalla_thailand_available_tours",
    "priority": 10,
    "body": {
        "sheet": {
            "sections": [
                {
                    "title": _("Trip Info"),
                    "groups": [
                        {
                            "fields": [
                                {"name": "name","string": _("Name"),"widget": "text", "required": True},
                                {
                                    "name": "supplier",
                                    "widget": "relation",
                                    "string": _("Supplier"),
                                    "displayField": "name",
                                    "multiSelect": False,
                                    "domain": {
                                        "filters": {
                                            "operator": "and",
                                            "filters": [
                                                {"field": "supplier", "operator": "eq", "value": True},
                                                {"field": "active", "operator": "eq", "value": True}
                                            ]
                                        }
                                    },
                                    "context": {
                                        "default_fields": {
                                            "supplier": True,
                                            "active": True
                                        }
                                    }
                                },
                                {"name": "destination",   "widget": "select",   "string": _("Destination")},
                                {"name": "activity_type", "widget": "select",   "string": _("Act. Type")},
                                {"name": "duration",      "widget": "select",   "string": _("Duration")},
                                {"name": "time",          "widget": "select",   "string": _("Time")},
                                {"name": "stop_activity", "widget": "select",   "string": _("Stop/Act.")},
                            ]
                        },
                        {
                            "fields": [
                                {"name": "quality",        "widget": "select", "string": _("Quality")},
                                {"name": "price_range",    "widget": "select", "string": _("Price Range")},
                                {"name": "lunch",          "widget": "select", "string": _("Lunch")},
                                {"name": "longtail_boat",  "widget": "select", "string": _("Longtail Boat")},
                                {"name": "national_park",  "widget": "select", "string": _("National Park")},
                                {"name": "no_of_pax",      "widget": "select", "string": _("No. of PAX")},
                            ]
                        },
                    ]
                }
            ],
            "tabs": [
                {
                    "title": _("Safety & Comfort"),
                    "sections": [
                        {
                            "groups": [
                                {
                                    "fields": [
                                        {"name": "motion_sickness",      "widget": "select", "string": _("Motion Sickness")},
                                        {"name": "weather_sensitivity",  "widget": "select", "string": _("Weather Sensitivity")},
                                        {"name": "children_eligibility", "widget": "select", "string": _("Children Eligibility")},
                                        {"name": "stability",            "widget": "select", "string": _("Stability")},
                                    ]
                                },
                                {
                                    "fields": [
                                        {"name": "action_adrenaline",  "widget": "select", "string": _("Action Adrenaline")},
                                        {"name": "romantic_honeymoon", "widget": "select", "string": _("Romantic / Honeymoon")},
                                        {"name": "smoker_friendly",    "widget": "select", "string": _("Smoker Friendly")},
                                        {"name": "mobility",           "widget": "select", "string": _("Mobility")},
                                    ]
                                },
                            ]
                        }
                    ]
                },
                {
                    "title": _("Boat & Water"),
                    "sections": [
                        {
                            "groups": [
                                {
                                    "fields": [
                                        {"name": "service_onboard", "widget": "select", "string": _("Service Onboard")},
                                        {"name": "boat_view",       "widget": "select", "string": _("Boat View")},
                                        {"name": "water_activity",  "widget": "select", "string": _("Water Act.")},
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "title": _("Pricing"),
                    "sections": [
                        {
                            "groups": [
                                {
                                    "fields": [
                                        {"name": "sell_prc_adult", "widget": "number", "string": _("Sell PRC Ad.")},
                                        {"name": "net_prc_adult",  "widget": "number", "string": _("Net PRC Ad.")},
                                        {"name": "min_markup",     "widget": "number", "string": _("Min. Markup")},
                                    ]
                                },
                                {
                                    "fields": [
                                        {"name": "sell_prc_child", "widget": "number", "string": _("Sell PRC Ch.")},
                                        {"name": "net_prc_child",  "widget": "number", "string": _("Net PRC Ch.")},
                                    ]
                                },
                            ]
                        }
                    ]
                },
                {
                    "title": _("Media"),
                    "sections": [
                        {
                            "groups": [
                                {
                                    "fields": [
                                        {"name": "whatsapp_catalog_link", "widget": "url",  "string": _("WhatsApp Catalog Link")},
                                        {"name": "video_link",            "widget": "url",  "string": _("Video Link")},
                                        {"name": "album",                 "widget": "text", "string": _("Album")},
                                        {"name": "note",                  "widget": "text", "string": _("Note")},
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "title": _("Attachments"),
                    "sections": [
                        {
                            "groups": [
                                {
                                    "fullWidth": True,
                                    "fields": [
                                        {"name": "main_image", "widget": "files", "string": _("Main Image"), "accept": "image/*","multiSelect": False,},
                                        {"name": "audio_ar", "widget": "files", "string": _("Audio (AR)"), "accept": "audio/*"},
                                        {"name": "audio_en", "widget": "files", "string": _("Audio (EN)"), "accept": "audio/*"},
                                        {"name": "video_ar", "widget": "files", "string": _("Video (AR)"), "accept": "video/*"},
                                        {"name": "video_en", "widget": "files", "string": _("Video (EN)"), "accept": "video/*"},
                                        {"name": "pics_ar",  "widget": "files", "string": _("Pictures (AR)"), "accept": "image/*"},
                                        {"name": "pics_en",  "widget": "files", "string": _("Pictures (EN)"), "accept": "image/*"},
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "title": _("Description"),
                    "sections": [
                        {
                            "title": "",
                            "groups": [
                                {
                                    "fullWidth": True,
                                    "fields": [
                                        {
                                            "name": "description",
                                            "string": "",
                                            "widget": "editor",
                                            "required": False,
                                            "readonly": False,
                                        },
                                    ]
                                }
                            ]
                        }
                    ]
                },
            ]
        }
    }
}


# =============================================================================
# SEARCH VIEW
# =============================================================================
available_trip_search_view = {
    "key": "yalla_available_trip_search",
    "name": "Available Trip Search",
    "model": "yalla_thailand.availabletrip",
    "view_type": "search",
    "module": "yalla_thailand",
    "menu_item": "yalla_thailand_available_tours",
    "priority": 10,
    "body": {
        "search": {
            "search_fields": ["name"],
            "filters": [
                {
                    "name": "smoker_allowed",
                    "string": _("Smoker Allowed"),
                    "filter": {"field": "smoker_friendly", "operator": "eq", "value": "allowed"},
                },
                {
                    "name": "kids_1plus",
                    "string": _("Kids 1+"),
                    "filter": {"field": "children_eligibility", "operator": "eq", "value": "1+"},
                },
                {
                    "name": "kids_3plus",
                    "string": _("Kids 3+"),
                    "filter": {"field": "children_eligibility", "operator": "in", "value": ["1+", "3+"]},
                },
            ],
            "group_by": [
                {"name": "destination",  "string": _("Destination")},
                {"name": "supplier",     "string": _("Supplier")},
                {"name": "activity_type","string": _("Act. Type")},
                {"name": "duration",     "string": _("Duration")},
                {"name": "quality",      "string": _("Quality")},
                {"name": "price_range",  "string": _("Price Range")},
                {"name": "time",         "string": _("Time")},
            ],
            "order_by": [{"field": "name", "direction": "asc"}],
        }
    }
}


# =============================================================================
# KANBAN VIEW
# =============================================================================
available_trip_kanban_view = {
    "key": "available_trip_kanban_view",
    "name": _("Available Tours"),
    "model": "yalla_thailand.availabletrip",
    "view_type": "kanban",
    "module": "yalla_thailand",
    "menu_item": "yalla_thailand_available_tours",
    "priority": 10,
    "body": {
        "kanban": {
            "id": "available-trip-kanban",
            "name": _("Available Tours"),
            "description": _("Trips grouped by destination"),
            "group_by": {"name": "destination", "tag": "field"},
            "card": {
                "header": {
                    "profile": {
                        
                        "title": {
                            "name": "name",
                            "tag": "field",
                            "widget": "text",
                            "string": _("Name"),
                            "required": True
                        }
                    },
                   "background_image": {"name": "main_image", "tag": "field", "widget": "image", "required": False, "readonly": True} # optional background image of the card
                },

            }
        }
    }
}
