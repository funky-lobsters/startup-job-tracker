from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from jobs.models import Job
from profiles.models import Profile

from .ai import AIError, recommend_jobs


def profile_is_empty(profile):
    return not any(
        [
            profile.background.strip(),
            profile.skills.strip(),
            profile.preferred_role_types,
            profile.preferred_locations.strip(),
            profile.preferred_stages,
        ]
    )


@login_required
def recommended_for_you(request):
    """Up to 5 jobs the AI thinks fit the logged-in user's profile, each with a one-sentence reason."""
    context = {"recommendations": [], "needs_profile": False, "no_jobs": False, "ai_error": False}

    profile = Profile.objects.filter(user=request.user).first()
    if profile is None or profile_is_empty(profile):
        context["needs_profile"] = True
        return render(request, "recommendations/list.html", context)

    jobs = Job.objects.select_related("company")
    if not jobs.exists():
        context["no_jobs"] = True
        return render(request, "recommendations/list.html", context)

    try:
        context["recommendations"] = recommend_jobs(profile, jobs)
    except AIError:
        context["ai_error"] = True
    return render(request, "recommendations/list.html", context)
