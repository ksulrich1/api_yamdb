from django.utils import timezone
from rest_framework import serializers


def year_validator(value):
    if value > timezone.now().year:
        raise serializers.ValidationError('Проверьте год')
    return value
