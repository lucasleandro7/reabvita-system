from django.db import models


PROFESSIONAL_CHOICES = [
    ('aline', 'Aline Leandro'),
    ('gustavo', 'Gustavo Leandro'),
    ('isabel', 'Isabel Novais'),
    ('stephane', 'Stephane Priscilla'),
]


SERVICE_TYPES = [
    ('avaliacao', 'Avaliação'),
    ('atendimento', 'Atendimento'),
]


class Appointment(models.Model):

    name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=20
    )

    email = models.EmailField()

    professional = models.CharField(
        max_length=20,
        choices=PROFESSIONAL_CHOICES
    )

    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_TYPES,
        default='avaliacao'
    )

    appointment_date = models.DateField()

    appointment_time = models.TimeField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f'{self.name} - '
            f'{self.get_professional_display()} - '
            f'{self.get_service_type_display()}'
        )