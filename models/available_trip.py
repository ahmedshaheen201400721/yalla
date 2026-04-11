# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext as _
from modules.base.models.base import BaseModel
from modules.base.fields import AttachmentManyToManyField, AttachmentForeignKeyField
from modules.base.decorators import action



class AvailableTrip(BaseModel):
    """
    Standalone model representing an available trip offered by Yalla Thailand.
    """

    # --- Choices ---
    DESTINATION_CHOICES = [
        ('phi_phi', 'Phi Phi'),
        ('james_bond', 'James Bond'),
        ('krabi_from_phuket', 'Krabi from Phuket'),
        ('krabi_from_krabi', 'Krabi from Krabi'),
        ('phang_nga', 'Phang Nga'),
        ('phuket', 'Phuket'),
        ('raya_coral', 'Raya & Coral'),
        ('similan', 'Similan'),
        ('bangkok', 'Bangkok'),
        ('koh_samui', 'Koh Samui'),
    ]

    MOTION_SICKNESS_CHOICES = [
        ('none', 'None'),
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('extreme', 'Extreme'),
    ]

    WEATHER_SENSITIVITY_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('extreme', 'Extreme'),
    ]

    CHILDREN_ELIGIBILITY_CHOICES = [
        ('1+', '1+'),
        ('3+', '3+'),
        ('8+', '8+'),
        ('12+', '12+'),
        ('16+', '16+'),
        ('conditional', 'Conditional'),
    ]

    ACTION_ADRENALINE_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]

    ROMANTIC_HONEYMOON_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]

    SMOKER_FRIENDLY_CHOICES = [
        ('allowed', 'Allowed'),
        ('conditional', 'Conditional'),
    ]

    PRICE_RANGE_CHOICES = [
        ('<2000', '<2000 THB'),
        ('2000-3500', '2000-3500 THB'),
        ('>3500', '>3500 THB'),
    ]

    LUNCH_CHOICES = [
        ('none', 'None'),
        ('island', 'Island'),
        ('onboard', 'Onbaord'),
        ('restaurant', 'Rest.'),
        ('extra', 'Extra'),
    ]

    STOP_ACTIVITY_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('9+', '9+'),
        ('custom', 'Custom'),
    ]

    DURATION_CHOICES = [
        ('3_hours', '3 Hours'),
        ('half_day', 'Half Day'),
        ('full_day', 'Full Day'),
        ('custom', 'Custom'),
    ]

    TIME_CHOICES = [
        ('early_morning', 'Early Morning'),
        ('early_bird', 'Early Bird'),
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('flexible', 'Flexible'),
        ('overnight', 'Overnight'),
    ]

    ACTIVITY_TYPE_CHOICES = [
        ('sea_trip', 'Sea Trip'),
        ('sea_adventure', 'Sea Adv.'),
        ('water_activity', 'Water Act.'),
        ('river_adventure', 'River Adv.'),
        ('land_adventure', 'Land Adv.'),
        ('evening_show', 'Evening Show'),
        ('city_tour', 'City Tour'),
    ]

    QUALITY_CHOICES = [
        ('economy', 'Economy'),
        ('average', 'Average'),
        ('conditional', 'Conditional'),
        ('premium', 'Premium'),
        ('high_end', 'High End'),
        ('luxury', 'Luxury'),
        ('private', 'Private'),
    ]

    SERVICE_ONBOARD_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]

    STABILITY_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]

    MOBILITY_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]

    BOAT_VIEW_CHOICES = [
        ('no_view', 'No View'),
        ('partial', 'Partial'),
        ('wide', 'Wide'),
        ('panoramic', 'Panoramic'),
    ]

    WATER_ACTIVITY_CHOICES = [
        ('none', 'None'),
        ('basic', 'Basic'),
        ('extra', 'Extra'),
        ('multiple', 'Multiple'),
    ]

    NO_OF_PAX_CHOICES = [
        ('<30', '<30'),
        ('30-60', '30-60'),
        ('>60', '>60'),
    ]

    LONGTAIL_BOAT_CHOICES = [
        ('none', 'None'),
        ('excluded', 'Excluded'),
        ('included', 'Included'),
        ('zodiac', 'Zodiac'),
    ]

    NATIONAL_PARK_CHOICES = [
        ('extra_200', 'Extra 200'),
        ('extra_300', 'Extra 300'),
        ('extra_400', 'Extra 400'),
        ('extra_500', 'Extra 500'),
        ('extra_600', 'Extra 600'),
        ('included', 'Included'),
    ]

    # --- Primary identifier ---
    name = models.CharField(
        _("Name"),
        max_length=255,
    )

    # --- Select fields matching final.csv columns ---
    destination = models.CharField(
        _("Destination"),
        max_length=50,
        choices=DESTINATION_CHOICES,
        null=True,
        blank=True,
    )
    motion_sickness = models.CharField(
        _("Motion Sickness"),
        max_length=20,
        choices=MOTION_SICKNESS_CHOICES,
        null=True,
        blank=True,
    )
    weather_sensitivity = models.CharField(
        _("Weather Sensitivity"),
        max_length=20,
        choices=WEATHER_SENSITIVITY_CHOICES,
        null=True,
        blank=True,
    )
    children_eligibility = models.CharField(
        _("Children Eligibility"),
        max_length=20,
        choices=CHILDREN_ELIGIBILITY_CHOICES,
        null=True,
        blank=True,
    )
    action_adrenaline = models.CharField(
        _("Action Adrenaline"),
        max_length=20,
        choices=ACTION_ADRENALINE_CHOICES,
        null=True,
        blank=True,
    )
    romantic_honeymoon = models.CharField(
        _("Romantic / Honeymoon"),
        max_length=20,
        choices=ROMANTIC_HONEYMOON_CHOICES,
        null=True,
        blank=True,
    )
    smoker_friendly = models.CharField(
        _("Smoker Friendly"),
        max_length=20,
        choices=SMOKER_FRIENDLY_CHOICES,
        null=True,
        blank=True,
    )
    price_range = models.CharField(
        _("Price Range"),
        max_length=20,
        choices=PRICE_RANGE_CHOICES,
        null=True,
        blank=True,
    )
    lunch = models.CharField(
        _("Lunch"),
        max_length=20,
        choices=LUNCH_CHOICES,
        null=True,
        blank=True,
    )
    stop_activity = models.CharField(
        _("Stop/Activity"),
        max_length=10,
        choices=STOP_ACTIVITY_CHOICES,
        null=True,
        blank=True,
    )
    duration = models.CharField(
        _("Duration"),
        max_length=20,
        choices=DURATION_CHOICES,
        null=True,
        blank=True,
    )
    time = models.CharField(
        _("Time"),
        max_length=20,
        choices=TIME_CHOICES,
        null=True,
        blank=True,
    )
    activity_type = models.CharField(
        _("Activity Type"),
        max_length=20,
        choices=ACTIVITY_TYPE_CHOICES,
        null=True,
        blank=True,
    )
    quality = models.CharField(
        _("Quality"),
        max_length=20,
        choices=QUALITY_CHOICES,
        null=True,
        blank=True,
    )
    service_onboard = models.CharField(
        _("Service Onboard"),
        max_length=20,
        choices=SERVICE_ONBOARD_CHOICES,
        null=True,
        blank=True,
    )
    stability = models.CharField(
        _("Stability"),
        max_length=20,
        choices=STABILITY_CHOICES,
        null=True,
        blank=True,
    )
    mobility = models.CharField(
        _("Mobility"),
        max_length=20,
        choices=MOBILITY_CHOICES,
        null=True,
        blank=True,
    )
    boat_view = models.CharField(
        _("Boat View"),
        max_length=20,
        choices=BOAT_VIEW_CHOICES,
        null=True,
        blank=True,
    )
    water_activity = models.CharField(
        _("Water Activity"),
        max_length=20,
        choices=WATER_ACTIVITY_CHOICES,
        null=True,
        blank=True,
    )
    no_of_pax = models.CharField(
        _("No. of PAX"),
        max_length=10,
        choices=NO_OF_PAX_CHOICES,
        null=True,
        blank=True,
    )
    longtail_boat = models.CharField(
        _("Longtail Boat"),
        max_length=20,
        choices=LONGTAIL_BOAT_CHOICES,
        null=True,
        blank=True,
    )
    national_park = models.CharField(
        _("National Park"),
        max_length=20,
        choices=NATIONAL_PARK_CHOICES,
        null=True,
        blank=True,
    )

    # --- Pricing ---
    sell_prc_adult = models.DecimalField(
        _("Sell PRC Ad."),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    net_prc_adult = models.DecimalField(
        _("Net PRC Ad."),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    sell_prc_child = models.DecimalField(
        _("Sell PRC Ch."),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    net_prc_child = models.DecimalField(
        _("Net PRC Ch."),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    min_markup = models.DecimalField(
        _("Min. Markup"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # --- Supplier ---
    supplier = models.ForeignKey(
        'base.Partner',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='yalla_supplied_trips',
        verbose_name=_("Supplier"),
    )

    # --- Media links ---
    whatsapp_catalog_link = models.URLField(
        _("WhatsApp Catalog Link"),
        max_length=500,
        null=True,
        blank=True,
    )
    video_link = models.URLField(
        _("Video Link"),
        max_length=500,
        null=True,
        blank=True,
    )
    album = models.CharField(
        _("Album"),
        max_length=255,
        null=True,
        blank=True,
    )
    note = models.TextField(
        _("Note"),
        null=True,
        blank=True,
    )
    description = models.TextField(
        _("Description"),
        null=True,
        blank=True,
    )

    # --- Attachment fields (AR/EN) ---
    audio_ar = AttachmentManyToManyField(
        upload_to='yalla_thailand/trips/audio_ar',
        allowed_types=['audio'],
        blank=True,
        related_name='availabletrip_audio_ar',
        related_query_name='availabletrip_audio_ar',
        verbose_name=_("Audio (AR)"),
    )
    audio_en = AttachmentManyToManyField(
        upload_to='yalla_thailand/trips/audio_en',
        allowed_types=['audio'],
        blank=True,
        related_name='availabletrip_audio_en',
        related_query_name='availabletrip_audio_en',
        verbose_name=_("Audio (EN)"),
    )
    video_ar = AttachmentManyToManyField(
        upload_to='yalla_thailand/trips/video_ar',
        allowed_types=['video'],
        blank=True,
        related_name='availabletrip_video_ar',
        related_query_name='availabletrip_video_ar',
        verbose_name=_("Video (AR)"),
    )
    video_en = AttachmentManyToManyField(
        upload_to='yalla_thailand/trips/video_en',
        allowed_types=['video'],
        blank=True,
        related_name='availabletrip_video_en',
        related_query_name='availabletrip_video_en',
        verbose_name=_("Video (EN)"),
    )
    pics_ar = AttachmentManyToManyField(
        upload_to='yalla_thailand/trips/pics_ar',
        allowed_types=['image'],
        blank=True,
        related_name='availabletrip_pics_ar',
        related_query_name='availabletrip_pics_ar',
        verbose_name=_("Pictures (AR)"),
    )
    pics_en = AttachmentManyToManyField(
        upload_to='yalla_thailand/trips/pics_en',
        allowed_types=['image'],
        blank=True,
        related_name='availabletrip_pics_en',
        related_query_name='availabletrip_pics_en',
        verbose_name=_("Pictures (EN)"),
    )
    main_image = AttachmentForeignKeyField(
        upload_to='yalla_thailand/trips/',
        allowed_types=['image'],
        blank=True, 
        null=True,
        help_text=_("Main image for the trip")
    )

    class Meta:
        verbose_name = "Available Trip"
        verbose_name_plural = "Available Trips"

    def __str__(self):
        return self.name

    @action
    def send_catalog_link_to_whatsapp(self, context: dict = None):
        """Send trip's WhatsApp catalog link to the active conversation."""
        conversation_id = (context or {}).get('conversation_id')
        if not conversation_id:
            return {
                'status': False,
                'open_mode': 'message',
                'message': _('No conversation context. Open this from a chat conversation.'),
            }

        from modules.chat.models import Conversation
        for trip in self:
            if not trip.whatsapp_catalog_link:
                return {
                    'status': False,
                    'open_mode': 'message',
                    'message': _('This trip has no WhatsApp catalog link.'),
                }
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return {
                    'status': False,
                    'open_mode': 'message',
                    'message': _('Conversation not found.'),
                }

            partner = conversation.social_partner
            if not partner or not getattr(partner, 'whatsapp_account', None):
                return {
                    'status': False,
                    'open_mode': 'message',
                    'message': _('No WhatsApp account linked to this contact.'),
                }

            result = partner.whatsapp_account.service.send_and_broadcast(
                partner=partner,
                content=trip.whatsapp_catalog_link,
                message_type='text',
                preview_url=True,
                conversation=conversation,
            )
            if result.get('success'):
                return {
                    'status': True,
                    'open_mode': 'message',
                    'message': _('Catalog link sent.'),
                }
            return {
                'status': False,
                'open_mode': 'message',
                'message': result.get('error', _('Failed to send.')),
            }
