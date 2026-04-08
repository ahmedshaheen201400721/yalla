# -*- coding: utf-8 -*-
# Tourism Voucher Sequence Registration (yalla_thailand)
from modules.base.models import Sequence
import logging

logger = logging.getLogger(__name__)

sequence, created = Sequence.objects.get_or_create(
    code="tourism.voucher",
    defaults={
        "name": "Tour Voucher Sequence",
        "prefix": "",
        "suffix": "",
        "padding": 5,
        "number_next": 1,
        "implementation": "no_gap",
        "reset_type": "never",
        "active": True,
    },
)

if created:
    logger.info(f"Created sequence: {sequence.name}")
    print(f"✅ Tour Voucher Sequence created (starting at {sequence.number_next})")
else:
    logger.info(f"Sequence already exists: {sequence.name}")
    print(f"✅ Tour Voucher Sequence already exists (next: {sequence.number_next})")
