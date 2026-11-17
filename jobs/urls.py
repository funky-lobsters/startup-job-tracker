from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    path("jobs/", views.job_list, name="list"),
    path("jobs/<int:pk>/", views.job_detail, name="detail"),
]
