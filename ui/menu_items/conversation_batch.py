from django.utils.translation import gettext as _


menu_dict = {
    "append_trips_action_omnichannel": {
        "_inherit": "chat_main_menu_omnichannel",
        "inheritance_operations": [
            {
                "operation": "append",
                "target": "actions",
                "content": {
                    "string": _("Trips"),
                    "icon": "Map",
                    "name": "get_trips_list",
                    "type": "server",
                    "as": "button",
                    "view_type": ["form"],
                    # "confirm_required": False,
                    # "allowed_groups": ["tourism.users"],
                },
            },
            {
                "operation": "remove",
                "target": "actions",
                "match": {"name": "get_full_contacts"}
            },
            {
                "operation": "remove",
                "target": "actions",
                "match": {"name": "get_sales_orders"}
            },
        ]
    }
}
