from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Job


@login_required
def job_list(request):
    """All jobs in one list, newest first. Logged-out visitors are sent to /login/."""
    jobs = Job.objects.select_related("company")  # one query for jobs and their companies
    return render(request, "jobs/job_list.html", {"jobs": jobs})


@login_required
def job_detail(request, pk):
    """Everything about one job. An unknown job id shows the normal "not found" page."""
    job = get_object_or_404(Job.objects.select_related("company"), pk=pk)
    return render(request, "jobs/job_detail.html", {"job": job})
