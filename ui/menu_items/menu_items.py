# -*- coding: utf-8 -*-
# Menu items for yalla_thailand module
from django.utils.translation import gettext as _


menu_dict = {
    "yalla_thailand_available_tours": {
        "name": _("Tours"),
        "icon": "Map",
        "module": "tourism",
        "model": "yalla_thailand.availabletrip",
        "sequence": 2,
        "view_types": "list,form,kanban",
        "parent_key":"tourism_config_menu",
        'actions' : [
                     {
                        "string": _("Send to WhatsApp"),
                        "name": "send_catalog_link_to_whatsapp",
                        "icon": "Send",
                       "type": "server",
                       "as": "button",
                       "confirm_required": False,
                    "view_type": ['kanban','list'],
                    }
        ],
    },
    
}
