from django.db import models

from apps.doctors.models import Doctor
from apps.patients.models import Patient


class PatientDoctorMapping(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="mappings")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="mappings")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-assigned_at", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["patient", "doctor"], name="unique_patient_doctor"),
        ]
        indexes = [models.Index(fields=["patient"]), models.Index(fields=["doctor"])]

    def __str__(self):
        return f"{self.patient} -> {self.doctor}"
