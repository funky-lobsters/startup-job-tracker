import logging
import os

from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe

logger = logging.getLogger(__name__)


def home(request):
    """Home page. The template shows whether the visitor is logged in."""
    return render(request, "core/home.html")


@never_cache
@require_safe
def health(request):
    """Public health check: which code version is running, and can we reach the database?

    Render sets RENDER_GIT_COMMIT (the full commit id) and RENDER_SERVICE_NAME on each deploy, so this
    shows whether staging and production run the same version. Returns 503 if the database is down.
    It reveals no secrets: only the short commit id, the service name and "ok"/"error".
    """
    commit = (os.environ.get("RENDER_GIT_COMMIT") or "unknown")[:7]
    service = os.environ.get("RENDER_SERVICE_NAME") or "local"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        database = "ok"
    except Exception as error:  # any database problem: report it, never crash
        # Log only the kind of error: the message could contain connection details.
        logger.warning("Health check: database unreachable (%s)", type(error).__name__)
        database = "error"
    healthy = database == "ok"
    return JsonResponse(
        {"status": "ok" if healthy else "error", "commit": commit, "service": service, "database": database},
        status=200 if healthy else 503,
    )
