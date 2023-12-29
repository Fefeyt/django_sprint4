from django.utils import timezone
from django.core.exceptions import ValidationError


def real_time(value):
    if value.date() < timezone.now().date():
        raise ValidationError('Нельзя публиковать записи в прошлом')
