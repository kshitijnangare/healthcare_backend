from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()

PATIENT = {
    "name": "John Doe", "age": 34, "gender": "M",
    "phone": "+911234567890", "address": "Mumbai", "medical_history": "None",
}


class PatientTests(APITestCase):
    def setUp(self):
        self.u1 = User.objects.create_user("u1@x.com", "Pass#12345", name="U1")
        self.u2 = User.objects.create_user("u2@x.com", "Pass#12345", name="U2")
        self.client.force_authenticate(self.u1)

    def test_crud(self):
        res = self.client.post("/api/patients/", PATIENT, format="json")
        self.assertEqual(res.status_code, 201)
        pid = res.data["id"]
        self.assertEqual(res.data["created_by"], self.u1.id)

        self.assertEqual(self.client.get("/api/patients/").data["count"], 1)
        self.assertEqual(self.client.get(f"/api/patients/{pid}/").status_code, 200)

        put = self.client.put(f"/api/patients/{pid}/", {**PATIENT, "age": 35}, format="json")
        self.assertEqual(put.status_code, 200)
        self.assertEqual(put.data["age"], 35)
        patch = self.client.patch(f"/api/patients/{pid}/", {"name": "Jane"}, format="json")
        self.assertEqual(patch.data["name"], "Jane")

        self.assertEqual(self.client.delete(f"/api/patients/{pid}/").status_code, 204)
        self.assertEqual(self.client.get(f"/api/patients/{pid}/").status_code, 404)

    def test_validation(self):
        res = self.client.post("/api/patients/", {**PATIENT, "age": 0, "phone": "abc"}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("age", res.data["errors"])
        self.assertIn("phone", res.data["errors"])
        res = self.client.post("/api/patients/", {}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_ownership_isolation(self):
        pid = self.client.post("/api/patients/", PATIENT, format="json").data["id"]
        self.client.force_authenticate(self.u2)
        self.assertEqual(self.client.get("/api/patients/").data["count"], 0)
        self.assertEqual(self.client.get(f"/api/patients/{pid}/").status_code, 404)
        self.assertEqual(self.client.put(f"/api/patients/{pid}/", PATIENT, format="json").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/patients/{pid}/").status_code, 404)

    def test_not_found_uses_error_shape(self):
        res = self.client.get("/api/patients/9999/")
        self.assertEqual(res.status_code, 404)
        self.assertFalse(res.data["success"])
