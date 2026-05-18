from django.urls import path

from .views import (
    index,
    get_available_times,
    cancel_appointment,
    schedule,
    dashboard,
    delete_appointment,
    professional_login,
    professional_logout,
)

urlpatterns = [

    path(
        '',
        index,
        name='index'
    ),

    path(
        'login/',
        professional_login,
        name='professional_login'
    ),

    path(
        'logout/',
        professional_logout,
        name='professional_logout'
    ),

    path(
        'available-times/',
        get_available_times,
        name='available_times'
    ),

    path(
        'cancel/',
        cancel_appointment,
        name='cancel'
    ),

    path(
        'schedule/',
        schedule,
        name='schedule'
    ),

    path(
        'dashboard/',
        dashboard,
        name='dashboard'
    ),

    path(
        'delete/<int:appointment_id>/',
        delete_appointment,
        name='delete_appointment'
    ),

]