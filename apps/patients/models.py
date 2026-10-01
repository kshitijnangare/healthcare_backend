from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

phone_validator = RegexValidator(
    r"^\+?[0-9\s\-]{7,15}$",
    "Enter a valid phone number (7-15 digits, optional leading +).",
)


class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    name = models.CharField(max_length=150)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(150)])
    gender = models.CharField(max_length=1, choices=Gender.choices)
    phone = models.CharField(max_length=20, validators=[phone_validator])
    address = models.TextField()
    medical_history = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patients"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["created_by", "-created_at"])]

    def __str__(self):
        return f"{self.name} ({self.age})"
