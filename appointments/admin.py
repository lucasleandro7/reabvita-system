from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'professional',
        'phone',
        'email',
        'appointment_date',
        'appointment_time',
    )

    search_fields = (
        'name',
        'email',
        'phone',
    )

    list_filter = (
        'professional',
        'appointment_date',
    )

    ordering = (
        'appointment_date',
        'appointment_time',
    )