from rest_framework import generics

from .models import Patient
from .serializers import PatientSerializer


class PatientListCreateView(generics.ListCreateAPIView):
    """GET: patients created by the current user. POST: create a patient."""

    serializer_class = PatientSerializer

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PUT / PATCH / DELETE. Other users' patients return 404."""

    serializer_class = PatientSerializer

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)
