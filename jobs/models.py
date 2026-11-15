from django.db import models


class Company(models.Model):
    """A startup (or VC firm) that posts jobs."""

    class Stage(models.TextChoices):
        PRE_SEED = "pre_seed", "Pre-seed"
        SEED = "seed", "Seed"
        SERIES_A = "series_a", "Series A"
        SERIES_B_PLUS = "series_b_plus", "Series B+"

    name = models.CharField(max_length=200, unique=True)
    website = models.URLField(blank=True)
    stage = models.CharField(max_length=20, choices=Stage.choices, blank=True)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class Job(models.Model):
    """One open role at a company. `apply_url` points to the original posting."""

    class RoleType(models.TextChoices):
        PRODUCT = "product", "Product"
        OPERATIONS = "operations", "Operations"
        STRATEGY = "strategy", "Strategy"
        VC_INVESTING = "vc_investing", "VC / Investing"
        OTHER = "other", "Other"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    role_type = models.CharField(max_length=20, choices=RoleType.choices, default=RoleType.OTHER)
    posted_date = models.DateField()
    apply_url = models.URLField(max_length=500)

    class Meta:
        ordering = ["-posted_date", "-id"]  # newest first
        constraints = [
            # Lets the seed command (and later imports) avoid creating the same job twice.
            models.UniqueConstraint(fields=["company", "title"], name="unique_job_title_per_company"),
        ]

    def __str__(self):
        return f"{self.title} at {self.company}"
