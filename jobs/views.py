from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from .models import Company, Job


@login_required
def job_list(request):
    """All jobs in one list, newest first, narrowed by optional filters in the URL.

    Filters: ?role=<role type>&location=<location>&stage=<company stage>. They combine
    (a job must match every chosen filter). An unknown value is ignored, so an old or
    mistyped link still shows jobs instead of an error. Logged-out visitors go to /login/.
    """
    jobs = Job.objects.select_related("company")  # one query for jobs and their companies
    locations = list(Job.objects.order_by("location").values_list("location", flat=True).distinct())

    role = request.GET.get("role", "")
    if role not in Job.RoleType.values:
        role = ""
    location = request.GET.get("location", "")
    if location not in locations:
        location = ""
    stage = request.GET.get("stage", "")
    if stage not in Company.Stage.values:
        stage = ""

    if role:
        jobs = jobs.filter(role_type=role)
    if location:
        jobs = jobs.filter(location=location)
    if stage:
        jobs = jobs.filter(company__stage=stage)

    return render(request, "jobs/job_list.html", {
        "jobs": jobs,
        "role_choices": Job.RoleType.choices,
        "stage_choices": Company.Stage.choices,
        "locations": locations,
        "selected": {"role": role, "location": location, "stage": stage},
        "filters_active": bool(role or location or stage),
    })


@login_required
def job_detail(request, pk):
    """Everything about one job. An unknown job id shows the normal "not found" page."""
    job = get_object_or_404(Job.objects.select_related("company"), pk=pk)
    return render(request, "jobs/job_detail.html", {"job": job})


@login_required
def company_list(request):
    """Every company, A to Z, with how many open jobs each has (counted in the same query)."""
    companies = Company.objects.annotate(job_count=Count("jobs")).order_by("name")
    return render(request, "jobs/company_list.html", {"companies": companies})


@login_required
def company_detail(request, pk):
    """One company: what it does, its stage, and all its open jobs (newest first).
    An unknown company id shows the normal "not found" page."""
    company = get_object_or_404(Company, pk=pk)
    jobs = company.jobs.all()  # Job's default ordering is newest first
    return render(request, "jobs/company_detail.html", {"company": company, "jobs": jobs})
