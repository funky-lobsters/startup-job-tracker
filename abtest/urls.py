from django.urls import path
from django.views.generic import RedirectView

from . import views

# 26fd193 = first 7 characters of `printf %s funky-lobsters | shasum` (the course's rule).
AB_HASH = "26fd193"

urlpatterns = [
    path(f"{AB_HASH}", views.ab_page, name="ab_page"),
    path(f"{AB_HASH}/click", views.ab_click, name="ab_click"),
    path(f"{AB_HASH}/stats", views.ab_stats, name="ab_stats"),
    # Someone typing a trailing slash still lands on the page (a redirect doesn't count as an impression).
    path(f"{AB_HASH}/", RedirectView.as_view(pattern_name="ab_page", permanent=False)),
]
