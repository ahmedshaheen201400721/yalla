from django.utils.translation import gettext as _

lead_form_yalla_thailand_batch = {
    "key": "lead_form_yalla_thailand_batch",
    "name": "CRM Lead Form - Yalla Thailand Patch",
    "model": "crm.lead",
    "view_type": "form",
    "priority": 21,
    "inherit_mode": "extension",
    "inherit_id": "crm_lead_form_view",
    "module": "crm",
    "inheritance_operations": [
        {
            "operation": "remove",
            "target": "action[name=create_sales_order]",
        },
        {
            "operation": "modify",
            "target": "tab[title=Campaign Tracking]",
            "content": {"allowed_groups": ["crm.managers"]}
        },
    ],
}
