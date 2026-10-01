from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.doctors.models import Doctor
from apps.patients.models import Patient

User = get_user_model()


class MappingTests(APITestCase):
    def setUp(self):
        self.u1 = User.objects.create_user("u1@x.com", "Pass#12345", name="U1")
        self.u2 = User.objects.create_user("u2@x.com", "Pass#12345", name="U2")
        self.patient = Patient.objects.create(
            name="P1", age=30, gender="F", phone="9999999999", address="A", created_by=self.u1
        )
        self.doctor = Doctor.objects.create(
            name="D1", specialization="ENT", email="d1@x.com", phone="8888888888",
            years_of_experience=5, created_by=self.u1,
        )
        self.client.force_authenticate(self.u1)

    def _assign(self):
        return self.client.post(
            "/api/mappings/", {"patient": self.patient.id, "doctor": self.doctor.id}, format="json"
        )

    def test_create_list_get_delete(self):
        res = self._assign()
        self.assertEqual(res.status_code, 201)
        mid = res.data["id"]

        self.assertEqual(self.client.get("/api/mappings/").data["count"], 1)

        detail = self.client.get(f"/api/mappings/{self.patient.id}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["doctors"][0]["doctor"]["id"], self.doctor.id)
        self.assertEqual(detail.data["doctors"][0]["mapping_id"], mid)

        self.assertEqual(self.client.delete(f"/api/mappings/{mid}/").status_code, 204)
        self.assertEqual(self.client.get("/api/mappings/").data["count"], 0)

    def test_duplicate_returns_409(self):
        self._assign()
        res = self._assign()
        self.assertEqual(res.status_code, 409)
        self.assertFalse(res.data["success"])

    def test_invalid_references(self):
        res = self.client.post("/api/mappings/", {"patient": 999, "doctor": self.doctor.id}, format="json")
        self.assertEqual(res.status_code, 400)
        res = self.client.post("/api/mappings/", {"patient": self.patient.id, "doctor": 999}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_cannot_map_another_users_patient(self):
        self.client.force_authenticate(self.u2)
        res = self._assign()
        self.assertEqual(res.status_code, 400)
        self.assertEqual(self.client.get(f"/api/mappings/{self.patient.id}/").status_code, 404)

    def test_cannot_delete_another_users_mapping(self):
        mid = self._assign().data["id"]
        self.client.force_authenticate(self.u2)
        self.assertEqual(self.client.delete(f"/api/mappings/{mid}/").status_code, 404)
        self.assertEqual(self.client.get("/api/mappings/").data["count"], 0)
