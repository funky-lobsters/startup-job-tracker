import os
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

User = get_user_model()
ENV = {"GRADER_ADMIN_PASSWORD": "admin-test-pass-123", "GRADER_MEMBER_PASSWORD": "member-test-pass-456"}


def run_seed():
    out, err = StringIO(), StringIO()
    call_command("seed", stdout=out, stderr=err)
    return out.getvalue(), err.getvalue()


class SeedCommandTests(TestCase):
    @patch.dict(os.environ, ENV)
    def test_creates_grader_accounts_that_can_log_in(self):
        run_seed()
        admin = User.objects.get(email="admin@example.com")
        member = User.objects.get(email="member@example.com")
        self.assertTrue(admin.is_superuser and admin.is_staff)
        self.assertFalse(member.is_staff or member.is_superuser)
        self.assertTrue(self.client.login(username="admin@example.com", password=ENV["GRADER_ADMIN_PASSWORD"]))
        self.assertTrue(self.client.login(username="member@example.com", password=ENV["GRADER_MEMBER_PASSWORD"]))

    @patch.dict(os.environ, ENV)
    def test_is_idempotent(self):
        run_seed()
        run_seed()
        run_seed()
        self.assertEqual(User.objects.count(), 2)

    @patch.dict(os.environ, ENV)
    def test_resets_changed_password_and_permissions(self):
        run_seed()
        member = User.objects.get(email="member@example.com")
        member.set_password("something-else-789")
        member.is_active = False
        member.save()
        run_seed()
        self.assertTrue(self.client.login(username="member@example.com", password=ENV["GRADER_MEMBER_PASSWORD"]))

    @patch.dict(os.environ, {**ENV, "GRADER_ADMIN_EMAIL": "Grader@Example.com"})
    def test_custom_email(self):
        run_seed()
        self.assertTrue(User.objects.filter(email="grader@example.com", is_superuser=True).exists())

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_passwords_skip_without_failing(self):
        out, err = run_seed()
        self.assertEqual(User.objects.count(), 0)
        self.assertIn("GRADER_ADMIN_PASSWORD is not set", err)
        self.assertIn("Seed complete", out)
