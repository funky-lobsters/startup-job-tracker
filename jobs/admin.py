from django.contrib import admin

from .models import Company, Job


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "stage", "location")
    list_filter = ("stage",)
    search_fields = ("name",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "role_type", "location", "posted_date")
    list_filter = ("role_type", "company__stage")
    search_fields = ("title", "company__name")
