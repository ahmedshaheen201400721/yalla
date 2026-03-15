from django.contrib import admin
from .models import AvailableTrip


@admin.register(AvailableTrip)
class AvailableTripAdmin(admin.ModelAdmin):
    pass
