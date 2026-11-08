from django.contrib import admin

from .models import Visitor


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    """Lets the team inspect A/B data and delete test visits before the graded bot run."""

    list_display = ("created_at", "variant", "source", "clicked_at")
    list_filter = ("variant", "source")
    search_fields = ("source", "referrer")
    readonly_fields = ("id", "variant", "referrer", "source", "created_at", "clicked_at")
