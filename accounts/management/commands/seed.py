"""`python manage.py seed`: create the grader accounts (and, later, demo data).

Idempotent: safe to run any number of times. It never duplicates accounts; it just makes sure
each grader account exists with the right password and permissions.

Passwords come from environment variables (never from the repo):
  GRADER_ADMIN_EMAIL     (default admin@example.com)
  GRADER_ADMIN_PASSWORD  required to create/update the admin account
  GRADER_MEMBER_EMAIL    (default member@example.com)
  GRADER_MEMBER_PASSWORD required to create/update the member account
If a password is missing, that account is skipped with a warning (the command still succeeds,
so a missing variable never stops the app from starting on Render).
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

GRADER_ACCOUNTS = [
    # (label, email env var, default email, password env var, is admin)
    ("admin", "GRADER_ADMIN_EMAIL", "admin@example.com", "GRADER_ADMIN_PASSWORD", True),
    ("member", "GRADER_MEMBER_EMAIL", "member@example.com", "GRADER_MEMBER_PASSWORD", False),
]


class Command(BaseCommand):
    help = "Create or update the grader accounts (and demo data). Safe to run repeatedly."

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        for label, email_var, default_email, password_var, is_admin in GRADER_ACCOUNTS:
            email = (os.environ.get(email_var) or default_email).strip().lower()
            password = os.environ.get(password_var)
            if not password:
                self.stderr.write(self.style.WARNING(f"Skipped {label} account: {password_var} is not set."))
                continue

            user = User.objects.filter(email__iexact=email).first()
            created = user is None
            if created:
                user = User(email=email)
            user.is_active = True
            user.is_staff = is_admin
            user.is_superuser = is_admin
            if created or not user.check_password(password):
                user.set_password(password)
            user.save()
            self.stdout.write(f"{'Created' if created else 'Checked'} {label} account: {email}")

        # Demo data (jobs, companies, ...) will be added here as those features are built.
        self.stdout.write(self.style.SUCCESS("Seed complete."))
