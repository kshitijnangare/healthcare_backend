from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models

from apps.patients.models import phone_validator


class Doctor(models.Model):
    name = models.CharField(max_length=150)
    specialization = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, validators=[phone_validator])
    years_of_experience = models.PositiveSmallIntegerField(validators=[MaxValueValidator(70)])
    hospital = models.CharField(max_length=200, blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctors"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"
