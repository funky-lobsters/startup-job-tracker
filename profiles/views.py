from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm
from .models import Profile


@login_required
def edit_profile(request):
    """Show and save the logged-in user's own profile.

    There is no profile id in the URL: the page always loads request.user's profile, so nobody
    can open or change someone else's.
    """
    profile = Profile.objects.filter(user=request.user).first() or Profile(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile saved")
            return redirect("profiles:edit")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "profiles/edit.html", {"form": form})
