from rest_framework import serializers

from apps.doctors.models import Doctor
from apps.doctors.serializers import DoctorSerializer
from apps.patients.models import Patient
from config.exceptions import Conflict

from .models import PatientDoctorMapping


class MappingSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "patient", "patient_name", "doctor", "doctor_name", "assigned_at")
        read_only_fields = ("id", "assigned_at")
        validators: list = []  # duplicate check done in validate() to return 409

    def validate_patient(self, patient):
        # Users can only assign doctors to their own patients.
        if patient.created_by_id != self.context["request"].user.id:
            raise serializers.ValidationError("Patient not found.")
        return patient

    def validate(self, attrs):
        if PatientDoctorMapping.objects.filter(patient=attrs["patient"], doctor=attrs["doctor"]).exists():
            raise Conflict("This doctor is already assigned to this patient.")
        return attrs


class AssignedDoctorSerializer(serializers.ModelSerializer):
    """A doctor assigned to a patient, plus the mapping id (needed for DELETE)."""

    mapping_id = serializers.IntegerField(source="id", read_only=True)
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ("mapping_id", "assigned_at", "doctor")
