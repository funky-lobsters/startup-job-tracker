import uuid

from django.db import models


class Visitor(models.Model):
    """One row per visitor to the A/B test page.

    - The row itself is the visitor's single **impression** (created_at = when they first saw the page).
    - clicked_at is their single **click** (empty until they click the button).
    - source/referrer record where they came from (HTTP Referer header on their first visit).
    """

    KUDOS = "kudos"
    THANKS = "thanks"
    VARIANTS = [(KUDOS, "kudos"), (THANKS, "thanks")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variant = models.CharField(max_length=10, choices=VARIANTS)
    referrer = models.TextField(blank=True, help_text="Raw Referer header on the first visit")
    source = models.CharField(
        max_length=255, db_index=True, help_text="Host name of the referrer, or 'direct' if none"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Impression time")
    clicked_at = models.DateTimeField(null=True, blank=True, help_text="Click time (at most one)")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.variant} from {self.source} at {self.created_at:%Y-%m-%d %H:%M}"
