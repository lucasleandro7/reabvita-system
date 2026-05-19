from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import date, datetime
from .models import Appointment


AVAILABLE_TIMES = [
    '08:00',
    '09:00',
    '10:00',
    '11:00',
    '14:00',
    '15:00',
    '16:00',
    '17:00',
    '18:00',
]


def get_user_professional(user):

    username = user.username.lower()

    if user.is_superuser:
        return None

    if 'aline' in username:
        return 'aline'

    if 'gustavo' in username:
        return 'gustavo'

    return None


def index(request):

    success = False
    error = False

    if request.method == 'POST':

        professional = request.POST['professional']
        appointment_date = request.POST['appointment_date']
        appointment_time = request.POST['appointment_time']

        selected_date = date.fromisoformat(appointment_date)

        if selected_date.weekday() == 6:

            error = 'Não atendemos aos domingos.'

        else:

            appointment_exists = Appointment.objects.filter(
                professional=professional,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            ).exists()

            same_patient = Appointment.objects.filter(
                email=request.POST['email'],
                appointment_date=appointment_date
            ).exists()

            if appointment_exists:

                error = 'Este horário já está ocupado!'

            elif same_patient:

                error = 'Você já possui uma consulta agendada neste dia.'

            else:

                Appointment.objects.create(
                    name=request.POST['name'],
                    phone=request.POST['phone'],
                    email=request.POST['email'],
                    professional=professional,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time
                )

                success = True

    return render(request, 'appointments/index.html', {
        'success': success,
        'error': error,
        'available_times': AVAILABLE_TIMES,
        'today': timezone.localdate().isoformat()
    })


def get_available_times(request):

    selected_date = request.GET.get('date')
    selected_professional = request.GET.get('professional')

    booked_times = Appointment.objects.filter(
        professional=selected_professional,
        appointment_date=selected_date
    ).values_list(
        'appointment_time',
        flat=True
    )

    booked_times = [
        time.strftime('%H:%M')
        for time in booked_times
    ]

    available_times = [
        time for time in AVAILABLE_TIMES
        if time not in booked_times
    ]

    today = timezone.localdate().isoformat()

    if selected_date == today:

        current_time = timezone.localtime().strftime('%H:%M')

        available_times = [
            time for time in available_times
            if time > current_time
        ]

    return JsonResponse({
        'available_times': available_times
    })


def cancel_appointment(request):

    appointments = []
    success = False

    if request.method == 'GET':

        email = request.GET.get('email')

        if email:

            appointments = Appointment.objects.filter(
                email=email
            )

    if request.method == 'POST':

        appointment_id = request.POST.get('appointment_id')

        Appointment.objects.filter(
            id=appointment_id
        ).delete()

        success = True

    return render(request, 'appointments/cancel.html', {
        'appointments': appointments,
        'success': success
    })


@login_required
def schedule(request):

    selected_date = request.GET.get('date')
    selected_professional = request.GET.get('professional')
    search = request.GET.get('search')

    user_professional = get_user_professional(request.user)

    if request.user.is_superuser:

        appointments = Appointment.objects.all()

    elif user_professional:

        appointments = Appointment.objects.filter(
            professional=user_professional
        )

    else:

        appointments = Appointment.objects.none()

    if selected_date:

        appointments = appointments.filter(
            appointment_date=selected_date
        )

    if selected_professional and request.user.is_superuser:

        appointments = appointments.filter(
            professional=selected_professional
        )

    if search:

        appointments = appointments.filter(
            name__icontains=search
        )

    appointments = appointments.order_by(
        'appointment_date',
        'appointment_time'
    )

    return render(request, 'appointments/schedule.html', {
        'appointments': appointments,
        'selected_date': selected_date,
        'selected_professional': selected_professional,
        'search': search
    })


@login_required
def dashboard(request):

    user_professional = get_user_professional(request.user)

    if request.user.is_superuser:

        appointments = Appointment.objects.all()

    elif user_professional:

        appointments = Appointment.objects.filter(
            professional=user_professional
        )

    else:

        appointments = Appointment.objects.none()

    total_appointments = appointments.count()

    today_appointments = appointments.filter(
        appointment_date=date.today()
    ).count()

    aline_appointments = appointments.filter(
        professional='aline'
    ).count()

    gustavo_appointments = appointments.filter(
        professional='gustavo'
    ).count()

    next_appointments = appointments.filter(
        appointment_date__gte=date.today()
    ).order_by(
        'appointment_date',
        'appointment_time'
    )[:5]

    return render(request, 'appointments/dashboard.html', {
        'total_appointments': total_appointments,
        'today_appointments': today_appointments,
        'aline_appointments': aline_appointments,
        'gustavo_appointments': gustavo_appointments,
        'next_appointments': next_appointments,
    })


@login_required
def delete_appointment(request, appointment_id):

    user_professional = get_user_professional(request.user)

    if request.user.is_superuser:

        appointment = Appointment.objects.get(
            id=appointment_id
        )

    elif user_professional:

        appointment = Appointment.objects.get(
            id=appointment_id,
            professional=user_professional
        )

    else:

        return redirect('/schedule/')

    appointment.delete()

    return redirect('/schedule/')


def professional_login(request):

    error = False

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('/dashboard/')

        else:

            error = True

    return render(request, 'appointments/login.html', {
        'error': error
    })


@login_required
def professional_logout(request):

    logout(request)

    return redirect('/')

def my_appointments(request):

    appointments = []

    if request.method == 'GET':

        email = request.GET.get('email')

        if email:

            appointments = Appointment.objects.filter(
                email=email
            ).order_by(
                'appointment_date',
                'appointment_time'
            )

    return render(request, 'appointments/my_appointments.html', {
        'appointments': appointments
    })