"""Fake demo companies and jobs for `python manage.py seed`.

All names and links are made up (example.com addresses), so graders and teammates have something to
browse before real data is imported (see issue #30). Safe to run many times: each company is matched by
name and each job by (company, title), so nothing is duplicated.
"""

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import Company, Job

Stage = Company.Stage
Role = Job.RoleType

# (name, stage, location, description)
COMPANIES = [
    ("Lanternfish Labs", Stage.SEED, "New York, NY", "Developer tools for data teams."),
    ("Harbor Health AI", Stage.SERIES_A, "Boston, MA", "AI-assisted scheduling for clinics."),
    ("Copperleaf Climate", Stage.SERIES_B_PLUS, "San Francisco, CA", "Software for carbon accounting."),
    ("Tidewater Ventures", Stage.SEED, "New Haven, CT", "Early-stage VC fund investing in Northeast startups."),
    ("Quillstack", Stage.PRE_SEED, "Remote", "Writing tools for legal teams."),
    ("Bramble Finance", Stage.SERIES_A, "New York, NY", "Cash-flow planning for small businesses."),
    ("Northpine Robotics", Stage.SERIES_B_PLUS, "Pittsburgh, PA", "Warehouse robots for mid-size retailers."),
    ("Saffron Kitchen OS", Stage.SEED, "Austin, TX", "Operations software for restaurant groups."),
    ("Meridian Learning", Stage.PRE_SEED, "Remote", "Cohort-based courses for career switchers."),
    ("Kestrel Mobility", Stage.SERIES_A, "Chicago, IL", "Fleet management for e-bike delivery."),
]

# (company name, title, location, role type, posted N days ago)
JOBS = [
    ("Lanternfish Labs", "Founding Product Manager", "New York, NY", Role.PRODUCT, 1),
    ("Lanternfish Labs", "Business Operations Associate", "New York, NY", Role.OPERATIONS, 6),
    ("Harbor Health AI", "Product Manager, Clinician Experience", "Boston, MA", Role.PRODUCT, 2),
    ("Harbor Health AI", "Strategy & Partnerships Lead", "Boston, MA", Role.STRATEGY, 9),
    ("Copperleaf Climate", "Senior Product Manager", "San Francisco, CA", Role.PRODUCT, 3),
    ("Copperleaf Climate", "Chief of Staff to the CEO", "San Francisco, CA", Role.STRATEGY, 12),
    ("Tidewater Ventures", "Investment Associate", "New Haven, CT", Role.VC_INVESTING, 1),
    ("Tidewater Ventures", "MBA Venture Fellow (part-time)", "Remote", Role.VC_INVESTING, 15),
    ("Quillstack", "Founder's Associate", "Remote", Role.STRATEGY, 4),
    ("Quillstack", "Growth Marketing Lead", "Remote", Role.OTHER, 20),
    ("Bramble Finance", "Product Manager, Payments", "New York, NY", Role.PRODUCT, 5),
    ("Bramble Finance", "Head of Finance & Operations", "New York, NY", Role.OPERATIONS, 18),
    ("Northpine Robotics", "Strategic Finance Manager", "Pittsburgh, PA", Role.STRATEGY, 7),
    ("Northpine Robotics", "Operations Manager, Deployments", "Pittsburgh, PA", Role.OPERATIONS, 11),
    ("Saffron Kitchen OS", "Product Operations Manager", "Austin, TX", Role.OPERATIONS, 8),
    ("Saffron Kitchen OS", "Customer Success Lead", "Austin, TX", Role.OTHER, 25),
    ("Meridian Learning", "Product Lead (first PM hire)", "Remote", Role.PRODUCT, 10),
    ("Meridian Learning", "Partnerships Manager", "Remote", Role.STRATEGY, 22),
    ("Kestrel Mobility", "Operations Lead, City Launches", "Chicago, IL", Role.OPERATIONS, 13),
    ("Kestrel Mobility", "Corporate Development Associate", "Chicago, IL", Role.VC_INVESTING, 30),
]


def slug(text):
    return "".join(ch if ch.isalnum() else "-" for ch in text.lower()).strip("-")


@transaction.atomic
def load_demo_jobs():
    """Create the demo companies and jobs if they don't exist yet. Returns (companies created, jobs created)."""
    today = timezone.localdate()
    companies = {}
    companies_created = jobs_created = 0

    for name, stage, location, description in COMPANIES:
        company, created = Company.objects.get_or_create(
            name=name,
            defaults={
                "stage": stage,
                "location": location,
                "description": description,
                "website": f"https://{slug(name)}.example.com",
            },
        )
        companies[name] = company
        companies_created += created

    for company_name, title, location, role_type, days_ago in JOBS:
        company = companies[company_name]
        _, created = Job.objects.get_or_create(
            company=company,
            title=title,
            defaults={
                "location": location,
                "role_type": role_type,
                "posted_date": today - timedelta(days=days_ago),
                "apply_url": f"{company.website}/careers/{slug(title)}",
            },
        )
        jobs_created += created

    return companies_created, jobs_created
