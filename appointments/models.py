from django.db import models

class Appointment(models.Model):

    PROFESSIONAL_CHOICES = [
        ('aline', 'Fisioterapia - Aline'),
        ('gustavo', 'Funcional - Gustavo'),
    ]

    name = models.CharField(max_length=100)

    phone = models.CharField(max_length=20)

    email = models.EmailField()

    professional = models.CharField(
        max_length=20,
        choices=PROFESSIONAL_CHOICES
    )

    appointment_date = models.DateField()

    appointment_time = models.TimeField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name