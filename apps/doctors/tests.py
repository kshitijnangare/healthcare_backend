from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()

DOCTOR = {
    "name": "Meera Rao", "specialization": "Cardiology", "email": "meera@hospital.com",
    "phone": "9876543210", "years_of_experience": 12, "hospital": "City Care",
}


class DoctorTests(APITestCase):
    def setUp(self):
        self.u1 = User.objects.create_user("u1@x.com", "Pass#12345", name="U1")
        self.u2 = User.objects.create_user("u2@x.com", "Pass#12345", name="U2")
        self.client.force_authenticate(self.u1)

    def test_crud_as_creator(self):
        res = self.client.post("/api/doctors/", DOCTOR, format="json")
        self.assertEqual(res.status_code, 201)
        did = res.data["id"]
        self.assertEqual(self.client.get(f"/api/doctors/{did}/").status_code, 200)
        put = self.client.put(f"/api/doctors/{did}/", {**DOCTOR, "years_of_experience": 13}, format="json")
        self.assertEqual(put.status_code, 200)
        self.assertEqual(self.client.delete(f"/api/doctors/{did}/").status_code, 204)

    def test_duplicate_email_rejected(self):
        self.client.post("/api/doctors/", DOCTOR, format="json")
        res = self.client.post("/api/doctors/", {**DOCTOR, "email": "MEERA@hospital.com"}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.data["errors"])

    def test_all_users_can_read_but_only_creator_can_modify(self):
        did = self.client.post("/api/doctors/", DOCTOR, format="json").data["id"]
        self.client.force_authenticate(self.u2)
        self.assertEqual(self.client.get("/api/doctors/").data["count"], 1)
        self.assertEqual(self.client.get(f"/api/doctors/{did}/").status_code, 200)
        self.assertEqual(self.client.put(f"/api/doctors/{did}/", DOCTOR, format="json").status_code, 403)
        self.assertEqual(self.client.delete(f"/api/doctors/{did}/").status_code, 403)
