from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Job


@login_required
def job_list(request):
    """All jobs in one list, newest first. Logged-out visitors are sent to /login/."""
    jobs = Job.objects.select_related("company")  # one query for jobs and their companies
    return render(request, "jobs/job_list.html", {"jobs": jobs})
