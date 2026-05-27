import os
import re
from twilio.rest import Client


def format_phone_to_whatsapp(phone):

    phone = re.sub(r'\D', '', phone)

    if phone.startswith('55'):

        return '+' + phone

    return '+55' + phone


def send_whatsapp_confirmation(appointment):

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_whatsapp = os.environ.get('TWILIO_WHATSAPP_FROM')

    if not account_sid or not auth_token or not from_whatsapp:
        return

    client = Client(account_sid, auth_token)

    phone = format_phone_to_whatsapp(appointment.phone)

    print(phone)

    message = (
        f"Olá, {appointment.name}! "
        f"Sua consulta na Reabvita foi agendada com sucesso. "
        f"Atendimento: {appointment.get_professional_display()}. "
        f"Data: {appointment.appointment_date}. "
        f"Horário: {appointment.appointment_time}."
    )

    client.messages.create(
        body=message,
        from_=from_whatsapp,
        to=f'whatsapp:+{phone.replace("+", "")}'
    )