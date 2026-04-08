from django.utils.translation import gettext as _

activity_form_yalla_thailand_batch = {
    "key": "activity_form_yalla_thailand_batch",
    "name": "Activity Form - Yalla Thailand Patch",
    "model": "notifications.activity",
    "view_type": "form",
    "priority": 20,
    "inherit_mode": "extension",
    "inherit_id": "notification_activity_form_view",
    "module": "notifications",
    "inheritance_operations": [
        {
            "operation": "modify",
            "target": "field[name=user_id]",
            "content": {
                "allowed_groups": ["crm.managers", "tourism.managers"]
            }
        }
    ]
}
