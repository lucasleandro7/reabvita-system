from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

from .models import Appointment
from .utils import send_whatsapp_confirmation


AVAILABLE_TIMES = {
    'aline': {
        'default': [
            '14:00',
            '15:00',
            '16:00',
            '17:00',
            '18:00',
        ],
        'friday': [
            '10:00',
            '11:00',
            '14:00',
            '15:00',
            '16:00',
            '17:00',
            '18:00',
        ],
    },
    'gustavo': {
        'default': [
            '16:00',
            '17:00',
            '18:00',
        ],
        'friday': [
            '16:00',
            '17:00',
            '18:00',
        ],
    },
}


def get_user_professional(user):

    username = user.username.lower()

    if user.is_superuser:
        return None

    if 'aline' in username:
        return 'aline'

    if 'gustavo' in username:
        return 'gustavo'

    return None


def get_professional_times(professional, selected_date):

    if not professional or not selected_date:
        return []

    if selected_date.weekday() == 4:
        return AVAILABLE_TIMES.get(
            professional,
            {}
        ).get('friday', [])

    return AVAILABLE_TIMES.get(
        professional,
        {}
    ).get('default', [])


def index(request):

    success = False
    error = False

    if request.method == 'POST':

        professional = request.POST['professional']
        service_type = request.POST['service_type']
        appointment_date = request.POST['appointment_date']
        appointment_time = request.POST['appointment_time']

        selected_date = date.fromisoformat(appointment_date)

        professional_times = get_professional_times(
            professional,
            selected_date
        )

        if selected_date.weekday() in [5, 6]:

            error = 'Não atendemos aos sábados e domingos.'

        elif appointment_time not in professional_times:

            error = 'Horário inválido para este profissional.'

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

                appointment = Appointment.objects.create(
                    name=request.POST['name'],
                    phone=request.POST['phone'],
                    email=request.POST['email'],
                    professional=professional,
                    service_type=service_type,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time
                )

                send_whatsapp_confirmation(appointment)

                success = True

    return render(request, 'appointments/index.html', {
        'success': success,
        'error': error,
        'available_times': [],
        'today': timezone.localdate().isoformat()
    })


def get_available_times(request):

    selected_date = request.GET.get('date')
    selected_professional = request.GET.get('professional')

    selected_date_obj = date.fromisoformat(selected_date)

    if selected_date_obj.weekday() in [5, 6]:

        return JsonResponse({
            'available_times': []
        })

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

    professional_times = get_professional_times(
        selected_professional,
        selected_date_obj
    )

    available_times = [
        time for time in professional_times
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


@login_required
def schedule(request):

    selected_date = request.GET.get('date')
    selected_professional = request.GET.get('professional')
    search = request.GET.get('search')

    user_professional = get_user_professional(request.user)

    if request.user.is_superuser:

        appointments = Appointment.objects.all()

    elif user_professional:

        appointments = Appointment.objects.all()

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

        appointments = Appointment.objects.all()

    else:

        appointments = Appointment.objects.none()

    total_appointments = appointments.count()

    today_appointments = appointments.filter(
        appointment_date=timezone.localdate()
    ).count()

    aline_appointments = appointments.filter(
        professional='aline'
    ).count()

    gustavo_appointments = appointments.filter(
        professional='gustavo'
    ).count()

    next_appointments = appointments.filter(
        appointment_date__gte=timezone.localdate()
    ).order_by(
        'appointment_date',
        'appointment_time'
)

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

    if request.user.is_superuser or user_professional:

        appointment = Appointment.objects.get(
            id=appointment_id
        )

    else:

        return redirect('/schedule/')

    appointment.delete()

    return redirect('/schedule/')


@login_required
def edit_appointment(request, appointment_id):

    user_professional = get_user_professional(request.user)

    if request.user.is_superuser or user_professional:

        appointment = Appointment.objects.get(
            id=appointment_id
        )

    else:

        return redirect('/schedule/')

    if request.method == 'POST':

        appointment.name = request.POST['name']
        appointment.phone = request.POST['phone']
        appointment.email = request.POST['email']
        appointment.professional = request.POST['professional']
        appointment.service_type = request.POST['service_type']
        appointment.appointment_date = request.POST['appointment_date']
        appointment.appointment_time = request.POST['appointment_time']

        appointment.save()

        return redirect('/schedule/')

    professional_times = get_professional_times(
        appointment.professional,
        appointment.appointment_date
    )

    return render(request, 'appointments/edit_appointment.html', {
        'appointment': appointment,
        'available_times': professional_times
    })


@login_required
def calendar_view(request):

    user_professional = get_user_professional(request.user)

    if request.user.is_superuser:

        appointments = Appointment.objects.all()

    elif user_professional:

        appointments = Appointment.objects.all()

    else:

        appointments = Appointment.objects.none()

    events = []

    for appointment in appointments:

        event_color = '#2563eb'

        if appointment.professional == 'gustavo':

            event_color = '#16a34a'

        if appointment.appointment_date < timezone.localdate():

            event_color = '#64748b'

        events.append({

            'title': (
                f'{str(appointment.appointment_time)[:5]} - '
                f'{appointment.name} '
                f'({appointment.get_professional_display()})'
            ),

            'start': f'{appointment.appointment_date}',

            'backgroundColor': event_color,

            'borderColor': event_color,

        })

    return render(request, 'appointments/calendar.html', {
        'events': events
    })


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


def create_admin_temp(request):

    if not User.objects.filter(
        username='lucasadmin123'
    ).exists():

        User.objects.create_superuser(
            username='lucasadmin123',
            email='seuemail@email.com',
            password='sua_senha_aqui'
        )

    return render(request, 'appointments/admin_created.html')