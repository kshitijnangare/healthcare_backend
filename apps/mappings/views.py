from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.patients.models import Patient

from .models import PatientDoctorMapping
from .serializers import AssignedDoctorSerializer, MappingSerializer


class MappingListCreateView(generics.ListCreateAPIView):
    """GET: mappings for the user's own patients. POST: assign a doctor to a patient."""

    serializer_class = MappingSerializer

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(
            patient__created_by=self.request.user
        ).select_related("patient", "doctor")


class MappingDetailView(APIView):
    """
    /api/mappings/<int:pk>/ is shared by two operations (as required by the spec):
      GET    -> pk is a *patient id*: list all doctors assigned to that patient
      DELETE -> pk is a *mapping id*: remove that assignment
    """

    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        mappings = patient.mappings.select_related("doctor")
        return Response(
            {
                "patient": {"id": patient.id, "name": patient.name},
                "doctors": AssignedDoctorSerializer(mappings, many=True).data,
            }
        )

    def delete(self, request, pk):
        mapping = get_object_or_404(
            PatientDoctorMapping, pk=pk, patient__created_by=request.user
        )
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
