import os
from unittest import mock

from django.contrib.auth import get_user_model
from django.db import OperationalError
from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_page_loads_for_anonymous_visitor(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You are not logged in")

    def test_home_page_shows_logged_in_user(self):
        user = get_user_model().objects.create_user(email="alice@example.com", password="s3cure-pass-123")
        self.client.force_login(user)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "You are logged in as")
        self.assertContains(response, "alice@example.com")

    def test_layout_is_mobile_friendly(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'name="viewport"')
        self.assertContains(response, "pico")


class HealthPageTests(TestCase):
    """/health/ shows the running version and whether the database works (#43)."""

    def test_ok_with_render_commit_and_service(self):
        env = {"RENDER_GIT_COMMIT": "8610813abcdef0123456789", "RENDER_SERVICE_NAME": "funky-lobsters"}
        with mock.patch.dict(os.environ, env):
            response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "commit": "8610813", "service": "funky-lobsters", "database": "ok"},
        )

    def test_unknown_commit_when_not_on_render(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("RENDER_GIT_COMMIT", None)
            os.environ.pop("RENDER_SERVICE_NAME", None)
            response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["commit"], "unknown")
        self.assertEqual(response.json()["service"], "local")

    def test_database_error_returns_503_without_crashing_or_leaking(self):
        secret_detail = "could not connect to postgresql://user:SECRETPASS@db.example.com"
        with mock.patch("core.views.connection.cursor", side_effect=OperationalError(secret_detail)):
            with self.assertLogs("core.views", level="WARNING") as logs:
                response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["database"], "error")
        self.assertNotIn("SECRETPASS", response.content.decode())
        self.assertNotIn("SECRETPASS", "\n".join(logs.output))

    def test_public_and_reveals_only_four_fields(self):
        response = self.client.get(reverse("health"))  # anonymous visitor, no login
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {"status", "commit", "service", "database"})
        self.assertIn("no-cache", response["Cache-Control"])

    def test_only_reads(self):
        self.assertEqual(self.client.post(reverse("health")).status_code, 405)
