from django.urls import path

from . import views

app_name = "recommendations"

urlpatterns = [
    path("recommendations/", views.recommended_for_you, name="list"),
]
