from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()
PASSWORD = "s3cure-pass-123"


class SignUpTests(TestCase):
    def test_signup_page_loads(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_account_and_logs_in(self):
        response = self.client.post(
            reverse("signup"),
            {"email": "New.Person@Example.com", "password1": PASSWORD, "password2": PASSWORD},
        )
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(User.objects.filter(email="new.person@example.com").exists())
        home = self.client.get(reverse("home"))
        self.assertContains(home, "You are logged in as")

    def test_signup_rejects_duplicate_email(self):
        User.objects.create_user(email="taken@example.com", password=PASSWORD)
        response = self.client.post(
            reverse("signup"),
            {"email": "TAKEN@example.com", "password1": PASSWORD, "password2": PASSWORD},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")
        self.assertEqual(User.objects.count(), 1)

    def test_signup_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("signup"),
            {"email": "x@example.com", "password1": PASSWORD, "password2": "different-pass-456"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())


class LoginLogoutTests(TestCase):
    def setUp(self):
        User.objects.create_user(email="member@example.com", password=PASSWORD)

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_with_email_and_password(self):
        response = self.client.post(reverse("login"), {"username": "member@example.com", "password": PASSWORD})
        self.assertRedirects(response, reverse("home"))
        self.assertContains(self.client.get(reverse("home")), "member@example.com")

    def test_login_email_is_case_insensitive(self):
        response = self.client.post(reverse("login"), {"username": "Member@Example.com", "password": PASSWORD})
        self.assertRedirects(response, reverse("home"))

    def test_login_fails_with_wrong_password(self):
        response = self.client.post(reverse("login"), {"username": "member@example.com", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(self.client.get(reverse("home")), "You are not logged in")

    def test_logout(self):
        self.client.login(username="member@example.com", password=PASSWORD)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
        self.assertContains(self.client.get(reverse("home")), "You are not logged in")
