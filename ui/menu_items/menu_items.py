# -*- coding: utf-8 -*-
# Menu items for yalla_thailand module
from django.utils.translation import gettext as _


menu_dict = {
    "yalla_thailand_available_trips": {
        "name": _("Trips"),
        "icon": "Map",
        "module": "tourism",
        "model": "yalla_thailand.availabletrip",
        "sequence": 2,
        "view_types": "list,form,kanban",
        "parent_key":"tourism_config_menu",
    },
    
}
