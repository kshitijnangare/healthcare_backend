from django.urls import reverse
from rest_framework.test import APITestCase


class AuthTests(APITestCase):
    payload = {"name": "Alice", "email": "Alice@Example.com", "password": "Str0ng#Pass123"}

    def test_register_success(self):
        res = self.client.post(reverse("register"), self.payload, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["user"]["email"], "alice@example.com")
        self.assertNotIn("password", res.data["user"])
        self.assertIn("access", res.data)

    def test_register_duplicate_email_case_insensitive(self):
        self.client.post(reverse("register"), self.payload, format="json")
        res = self.client.post(
            reverse("register"), {**self.payload, "email": "alice@example.COM"}, format="json"
        )
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.data["success"])
        self.assertIn("email", res.data["errors"])

    def test_register_weak_password_and_bad_email(self):
        res = self.client.post(
            reverse("register"), {"name": "A", "email": "nope", "password": "123"}, format="json"
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.data["errors"])
        self.assertIn("password", res.data["errors"])

    def test_login_success_and_failure(self):
        self.client.post(reverse("register"), self.payload, format="json")
        ok = self.client.post(
            reverse("login"),
            {"email": "alice@example.com", "password": self.payload["password"]},
            format="json",
        )
        self.assertEqual(ok.status_code, 200)
        self.assertIn("access", ok.data)
        self.assertIn("refresh", ok.data)
        bad = self.client.post(
            reverse("login"), {"email": "alice@example.com", "password": "wrong"}, format="json"
        )
        self.assertEqual(bad.status_code, 401)
        self.assertEqual(bad.data["message"], "Invalid email or password.")

    def test_protected_endpoint_requires_token(self):
        self.assertEqual(self.client.get("/api/patients/").status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid")
        self.assertEqual(self.client.get("/api/patients/").status_code, 401)
