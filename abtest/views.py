"""A/B test page (course requirement). Spec: docs/context/course-requirements.md, "A/B test page" + addendum.

Flow:
- GET  /26fd193        first visit: pick kudos/thanks at random, record impression + traffic source, set cookie.
                       later visits (cookie present): same variant, nothing new recorded.
- POST /26fd193/click  records the visitor's first click only, then redirects back to the page.
- GET  /26fd193/stats  live JSON counts and the "preferred" variant.
"""

import random
import uuid
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

import yaml
from django.conf import settings
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Visitor

COOKIE_NAME = "ab_visitor"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # one year
VARIANTS = [Visitor.KUDOS, Visitor.THANKS]


@lru_cache(maxsize=1)
def team_nicknames():
    """Members' course nicknames, read from docs/mgt656/team.yaml (single source of truth)."""
    path = Path(settings.BASE_DIR) / "docs" / "mgt656" / "team.yaml"
    data = yaml.safe_load(path.read_text()) or {}
    return [m["nickname"] for m in data.get("members", []) if m.get("nickname")]


def source_from_referrer(referrer):
    """'https://www.law.yale.edu/page' -> 'law.yale.edu'; empty or unreadable -> 'direct'."""
    try:
        host = (urlparse(referrer.strip()).hostname or "").lower()
    except ValueError:
        host = ""
    if host.startswith("www."):
        host = host[4:]
    return host[:255] or "direct"


def current_visitor(request):
    """The Visitor for this browser's cookie, or None if new (or the row was purged)."""
    raw = request.COOKIES.get(COOKIE_NAME)
    if not raw:
        return None
    try:
        return Visitor.objects.filter(pk=uuid.UUID(raw)).first()
    except ValueError:
        return None


@never_cache
@require_GET
def ab_page(request):
    visitor = current_visitor(request)
    is_new = visitor is None
    if is_new:
        referrer = request.META.get("HTTP_REFERER", "")[:2048]
        visitor = Visitor.objects.create(
            variant=random.choice(VARIANTS),
            referrer=referrer,
            source=source_from_referrer(referrer),
        )

    response = render(
        request,
        "abtest/page.html",
        {"visitor": visitor, "nicknames": team_nicknames(), "clicked": visitor.clicked_at is not None},
    )
    if is_new:
        response.set_cookie(
            COOKIE_NAME, str(visitor.pk), max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax",
            secure=request.is_secure(),
        )
    return response


# CSRF protection is off for this one harmless counter so that a click is never lost to a CSRF error.
# It's still safe: the visitor cookie is SameSite=Lax, so other sites can't make a click count.
@csrf_exempt
@require_POST
def ab_click(request):
    visitor = current_visitor(request)
    if visitor is not None and visitor.clicked_at is None:
        # update() with a filter makes "at most one click" hold even for double-clicks.
        Visitor.objects.filter(pk=visitor.pk, clicked_at__isnull=True).update(clicked_at=timezone.now())
    return redirect("ab_page")


def _counts(queryset):
    """{"kudos": {"impressions": n, "clicks": n}, "thanks": {...}} for a set of visitors."""
    rows = queryset.values("variant").annotate(
        impressions=Count("pk"), clicks=Count("pk", filter=Q(clicked_at__isnull=False))
    )
    counts = {v: {"impressions": 0, "clicks": 0} for v in VARIANTS}
    for row in rows:
        counts[row["variant"]] = {"impressions": row["impressions"], "clicks": row["clicks"]}
    return counts


def _rate(c):
    return c["clicks"] / c["impressions"] if c["impressions"] else 0.0


@never_cache
@require_GET
def ab_stats(request):
    counts = _counts(Visitor.objects.all())
    rates = {v: _rate(counts[v]) for v in VARIANTS}
    # Higher click rate wins; a tie (including no data yet) goes to kudos.
    preferred = Visitor.THANKS if rates[Visitor.THANKS] > rates[Visitor.KUDOS] else Visitor.KUDOS

    sources = {}
    for source in Visitor.objects.values_list("source", flat=True).distinct().order_by("source"):
        sources[source] = _counts(Visitor.objects.filter(source=source))

    return JsonResponse(
        {
            "preferred": preferred,
            **counts,
            "click_rates": {v: round(r, 4) for v, r in rates.items()},
            "sources": sources,
        }
    )
