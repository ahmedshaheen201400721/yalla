# -*- coding: utf-8 -*-
"""
Access rights for yalla_thailand module.
Format: [view, add, change, delete] as [0/1, 0/1, 0/1, 0/1]
"""

# Permission patterns for convenience
PERMISSION_PATTERNS = {
    'NONE': [0, 0, 0, 0],           # No access
    'VIEW_ONLY': [1, 0, 0, 0],      # View only
    'MANAGE': [1, 1, 1, 0],         # Manage but no delete
    'FULL': [1, 1, 1, 1],           # Full access
}

MODEL_PERMISSIONS = [
    # AvailableTrip — catalog of trips offered by Yalla Thailand
    {'model': 'yalla_thailand.availabletrip', 'group': 'tourism.users', 'permissions': PERMISSION_PATTERNS['FULL']},
    # {'model': 'yalla_thailand.availabletrip', 'group': 'yalla_thailand.trips', 'permissions': PERMISSION_PATTERNS['FULL']},
]

# Example using patterns:
# {
#     'model': 'yalla_thailand.modelname',
#     'group': 'yalla_thailand.users',
#     'permissions': PERMISSION_PATTERNS['MANAGE'],
# }
