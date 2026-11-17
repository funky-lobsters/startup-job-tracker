from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    path("jobs/", views.job_list, name="list"),
    path("jobs/<int:pk>/", views.job_detail, name="detail"),
    path("companies/", views.company_list, name="company_list"),
    path("companies/<int:pk>/", views.company_detail, name="company_detail"),
]
