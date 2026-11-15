from django.conf import settings
from django.db import models

# Same keys as the job filters (issue #26), so recommendations (#32) can compare a profile with jobs.
ROLE_TYPE_CHOICES = [
    ("product", "Product"),
    ("operations", "Operations"),
    ("strategy", "Strategy"),
    ("vc_investing", "VC / Investing"),
    ("other", "Other"),
]
STAGE_CHOICES = [
    ("pre_seed", "Pre-seed"),
    ("seed", "Seed"),
    ("series_a", "Series A"),
    ("series_b_plus", "Series B+"),
]


class Profile(models.Model):
    """A job seeker's background and preferences. One per user; the AI recommendations (#32) read it."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    background = models.TextField(blank=True, help_text="Your education and work experience, in a few sentences.")
    skills = models.TextField(blank=True, help_text="For example: financial modeling, SQL, customer research.")
    preferred_role_types = models.JSONField(default=list, blank=True)  # list of ROLE_TYPE_CHOICES keys
    preferred_locations = models.CharField(
        max_length=300, blank=True, help_text="Comma-separated, for example: New York, Boston, Remote."
    )
    preferred_stages = models.JSONField(default=list, blank=True)  # list of STAGE_CHOICES keys
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user}"

    def role_type_labels(self):
        labels = dict(ROLE_TYPE_CHOICES)
        return [labels[key] for key in self.preferred_role_types if key in labels]

    def stage_labels(self):
        labels = dict(STAGE_CHOICES)
        return [labels[key] for key in self.preferred_stages if key in labels]
