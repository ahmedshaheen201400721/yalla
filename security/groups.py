# -*- coding: utf-8 -*-
"""
Security groups for yalla_thailand module

This file defines all security groups for the yalla_thailand module.
Groups are synced to the database using the sync_groups management command.
"""

GROUPS = [
    {
        'name': 'Yalla_thailand Hotels',
        'technical_name': 'yalla_thailand.hotels',
        'category': 'Yalla_thailand',
        'description': 'Manage all yalla_thailand hotels',
    },
    {
        'name': 'Yalla_thailand transport',
        'technical_name': 'yalla_thailand.transport',
        'category': 'Yalla_thailand',
        'description': 'Manage all yalla_thailand transport',
    },
    {
        'name': 'Yalla_thailand trips',
        'technical_name': 'yalla_thailand.trips',
        'category': 'Yalla_thailand',
        'description': 'Manage all yalla_thailand trips',
    }
]
