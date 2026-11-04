from django.shortcuts import render


def home(request):
    """Home page. The template shows whether the visitor is logged in."""
    return render(request, "core/home.html")
