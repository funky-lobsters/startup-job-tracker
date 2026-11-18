import os
from datetime import date
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Company, Job

User = get_user_model()
PASSWORD = "s3cure-pass-123"


def make_job(title, company="Lanternfish Labs", posted=date(2026, 11, 10), **extra):
    company, _ = Company.objects.get_or_create(name=company, defaults={"stage": Company.Stage.SEED})
    fields = {
        "location": "New York, NY",
        "role_type": Job.RoleType.PRODUCT,
        "apply_url": "https://lanternfish-labs.example.com/careers/pm",
        **extra,
    }
    return Job.objects.create(company=company, title=title, posted_date=posted, **fields)


class JobListTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="seeker@example.com", password=PASSWORD)
        self.url = reverse("jobs:list")

    def test_url_is_jobs(self):
        self.assertEqual(self.url, "/jobs/")

    def test_logged_out_visitor_is_sent_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next=/jobs/")

    def test_logged_in_user_sees_every_job_with_its_details(self):
        make_job("Founding Product Manager", location="Remote", role_type=Job.RoleType.PRODUCT)
        make_job("Investment Associate", company="Tidewater Ventures", role_type=Job.RoleType.VC_INVESTING)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for text in ["Founding Product Manager", "Lanternfish Labs", "Remote", "Product",
                     "Investment Associate", "Tidewater Ventures", "VC / Investing", "Nov 10, 2026"]:
            self.assertContains(response, text)
        self.assertNotContains(response, "No jobs yet")

    def test_jobs_are_newest_first(self):
        make_job("Older role", posted=date(2026, 11, 1))
        make_job("Newest role", posted=date(2026, 11, 12))
        make_job("Middle role", posted=date(2026, 11, 5))
        self.client.force_login(self.user)
        titles = [job.title for job in self.client.get(self.url).context["jobs"]]
        self.assertEqual(titles, ["Newest role", "Middle role", "Older role"])

    def test_apply_link_opens_original_posting_in_new_tab(self):
        make_job("Founding Product Manager", apply_url="https://lanternfish-labs.example.com/careers/pm")
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<a href="https://lanternfish-labs.example.com/careers/pm" target="_blank" rel="noopener noreferrer" role="button">Apply</a>',
            html=True,
        )

    def test_each_job_title_links_to_its_detail_page(self):
        job = make_job("Founding Product Manager")
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, f'<a href="/jobs/{job.pk}/">Founding Product Manager</a>', html=True)

    def test_empty_state(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, "No jobs yet")
        self.assertNotContains(response, 'class="job"')

    def test_jobs_link_in_navigation_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("home"))
        self.assertContains(response, '<a href="/jobs/">Jobs</a>', html=True)

    def test_list_uses_a_fixed_number_of_queries(self):
        for i in range(5):
            make_job(f"Role {i}", company=f"Company {i}")
        self.client.force_login(self.user)
        # Session + user + locations for the filter dropdown + one jobs query that also
        # loads companies (no extra query per job).
        with self.assertNumQueries(4):
            self.client.get(self.url)


class JobFilterTests(TestCase):
    """Issue #26: filter /jobs/ by role type, location and company stage."""

    def setUp(self):
        self.user = User.objects.create_user(email="seeker@example.com", password=PASSWORD)
        self.client.force_login(self.user)
        Company.objects.create(name="Seedling AI", stage=Company.Stage.SEED)
        Company.objects.create(name="Bigco Robotics", stage=Company.Stage.SERIES_B_PLUS)
        make_job("Seed PM in NYC", company="Seedling AI", location="New York, NY",
                 role_type=Job.RoleType.PRODUCT)
        make_job("Seed Ops in Boston", company="Seedling AI", location="Boston, MA",
                 role_type=Job.RoleType.OPERATIONS)
        make_job("Late PM in Boston", company="Bigco Robotics", location="Boston, MA",
                 role_type=Job.RoleType.PRODUCT)

    def titles(self, query):
        response = self.client.get("/jobs/" + query)
        self.assertEqual(response.status_code, 200)
        return sorted(job.title for job in response.context["jobs"])

    def test_page_has_three_dropdowns_with_their_options(self):
        response = self.client.get("/jobs/")
        for name in ["role", "location", "stage"]:
            self.assertContains(response, f'<select name="{name}">')
        for option in ["Product", "Operations", "Strategy", "VC / Investing", "Other",
                       "New York, NY", "Boston, MA",
                       "Pre-seed", "Seed", "Series A", "Series B+"]:
            self.assertContains(response, f">{option}</option>")

    def test_no_filters_shows_every_job_and_no_clear_link(self):
        response = self.client.get("/jobs/")
        self.assertEqual(len(response.context["jobs"]), 3)
        self.assertNotContains(response, "Clear filters")

    def test_filter_by_role_only(self):
        self.assertEqual(self.titles("?role=product"), ["Late PM in Boston", "Seed PM in NYC"])

    def test_filter_by_location_only(self):
        self.assertEqual(self.titles("?location=Boston%2C+MA"), ["Late PM in Boston", "Seed Ops in Boston"])

    def test_filter_by_stage_only(self):
        self.assertEqual(self.titles("?stage=seed"), ["Seed Ops in Boston", "Seed PM in NYC"])

    def test_two_filters_combined(self):
        self.assertEqual(self.titles("?role=product&stage=seed"), ["Seed PM in NYC"])
        self.assertEqual(self.titles("?location=Boston%2C+MA&stage=series_b_plus"), ["Late PM in Boston"])

    def test_all_three_filters_combined(self):
        self.assertEqual(self.titles("?role=operations&location=Boston%2C+MA&stage=seed"),
                         ["Seed Ops in Boston"])

    def test_chosen_filters_stay_selected_so_the_url_can_be_shared(self):
        response = self.client.get("/jobs/?role=product&stage=seed")
        self.assertContains(response, '<option value="product" selected>Product</option>', html=True)
        self.assertContains(response, '<option value="seed" selected>Seed</option>', html=True)
        self.assertContains(response, '<form method="get" action="/jobs/" id="job-filters">')

    def test_clear_filters_link_goes_back_to_the_full_list(self):
        response = self.client.get("/jobs/?role=product")
        self.assertContains(response, '<a href="/jobs/" id="clear-filters">Clear filters</a>', html=True)

    def test_no_results_message(self):
        response = self.client.get("/jobs/?role=vc_investing")
        self.assertContains(response, "No jobs match these filters")
        self.assertNotContains(response, 'class="job"')
        self.assertNotContains(response, "No jobs yet")

    def test_unknown_filter_values_are_ignored(self):
        self.assertEqual(len(self.titles("?role=astronaut&stage=ipo&location=Mars")), 3)


class JobDetailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="seeker@example.com", password=PASSWORD)
        self.job = make_job(
            "Founding Product Manager",
            location="Remote",
            role_type=Job.RoleType.PRODUCT,
            posted=date(2026, 11, 10),
            apply_url="https://lanternfish-labs.example.com/careers/pm",
        )
        self.url = reverse("jobs:detail", args=[self.job.pk])

    def test_url_is_jobs_slash_id(self):
        self.assertEqual(self.url, f"/jobs/{self.job.pk}/")

    def test_logged_out_visitor_is_sent_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next=/jobs/{self.job.pk}/")

    def test_shows_every_detail_of_the_job(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Founding Product Manager</h1>", html=True)
        for text in ["Lanternfish Labs", "Remote", "Product", "Seed", "Nov 10, 2026"]:
            self.assertContains(response, text)

    def test_company_name_links_to_company_page(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            f'<p class="company-name"><a href="/companies/{self.job.company_id}/">Lanternfish Labs</a></p>',
            html=True,
        )

    def test_company_description_and_website_shown_when_present(self):
        Company.objects.filter(pk=self.job.company_id).update(
            description="We build tools for fishing fleets.", website="https://lanternfish-labs.example.com",
        )
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, "We build tools for fishing fleets.")
        self.assertContains(
            response,
            '<a href="https://lanternfish-labs.example.com" target="_blank" rel="noopener noreferrer">Company website</a>',
            html=True,
        )

    def test_company_section_hidden_when_no_description_or_website(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertNotContains(response, "About Lanternfish Labs")

    def test_missing_company_stage_says_not_listed(self):
        Company.objects.filter(pk=self.job.company_id).update(stage="")
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, "Not listed")

    def test_apply_button_opens_original_posting_in_new_tab(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<a href="https://lanternfish-labs.example.com/careers/pm" target="_blank" rel="noopener noreferrer" role="button">Apply</a>',
            html=True,
        )

    def test_unknown_job_shows_not_found(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("jobs:detail", args=[self.job.pk + 999]))
        self.assertEqual(response.status_code, 404)

    def test_page_has_link_back_to_all_jobs(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{reverse("jobs:list")}"')

    def test_detail_uses_a_fixed_number_of_queries(self):
        self.client.force_login(self.user)
        # Session + user + one query for the job and its company.
        with self.assertNumQueries(3):
            self.client.get(self.url)


class CompanyPageTests(TestCase):
    """Issue #27: company list and company profile pages."""

    def setUp(self):
        self.user = User.objects.create_user(email="seeker@example.com", password=PASSWORD)
        self.zeta = Company.objects.create(
            name="Zeta Health", stage=Company.Stage.SERIES_A, location="Boston, MA",
            website="https://zeta-health.example.com", description="Care navigation for clinics. " * 10,
        )
        self.acme = Company.objects.create(name="Acme Climate", stage=Company.Stage.PRE_SEED)
        self.empty = Company.objects.create(name="Mango Fintech")
        make_job("Chief of Staff", company="Zeta Health", posted=date(2026, 11, 1))
        make_job("Product Lead", company="Zeta Health", posted=date(2026, 11, 12))
        make_job("Founding Ops", company="Acme Climate")

    def test_urls(self):
        self.assertEqual(reverse("jobs:company_list"), "/companies/")
        self.assertEqual(reverse("jobs:company_detail", args=[self.zeta.pk]), f"/companies/{self.zeta.pk}/")

    def test_logged_out_visitor_is_sent_to_login(self):
        for url in ["/companies/", f"/companies/{self.zeta.pk}/"]:
            self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}")

    def test_list_shows_every_company_sorted_by_name_with_stage_and_job_count(self):
        self.client.force_login(self.user)
        response = self.client.get("/companies/")
        self.assertEqual([c.name for c in response.context["companies"]],
                         ["Acme Climate", "Mango Fintech", "Zeta Health"])
        for text in ["Series A", "2 open jobs", "Pre-seed", "1 open job", "Stage not listed", "0 open jobs",
                     "Care navigation for clinics."]:
            self.assertContains(response, text)
        self.assertContains(response, f'<a href="/companies/{self.zeta.pk}/">Zeta Health</a>', html=True)

    def test_list_description_is_shortened_to_one_line(self):
        self.client.force_login(self.user)
        response = self.client.get("/companies/")
        self.assertNotContains(response, self.zeta.description.strip())
        self.assertContains(response, "…")

    def test_list_uses_a_fixed_number_of_queries(self):
        for i in range(5):
            make_job(f"Role {i}", company=f"Extra Co {i}")
        self.client.force_login(self.user)
        # Session + user + one query for companies with their job counts.
        with self.assertNumQueries(3):
            self.client.get("/companies/")

    def test_detail_shows_company_info_and_its_jobs_newest_first(self):
        self.client.force_login(self.user)
        response = self.client.get(f"/companies/{self.zeta.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Zeta Health</h1>", html=True)
        for text in ["Care navigation for clinics.", "Series A", "Boston, MA", "Open jobs (2)"]:
            self.assertContains(response, text)
        self.assertContains(
            response,
            '<a href="https://zeta-health.example.com" target="_blank" rel="noopener noreferrer">https://zeta-health.example.com</a>',
            html=True,
        )
        self.assertEqual([j.title for j in response.context["jobs"]], ["Product Lead", "Chief of Staff"])
        self.assertNotContains(response, "Founding Ops")  # another company's job

    def test_detail_with_missing_details_and_no_jobs(self):
        self.client.force_login(self.user)
        response = self.client.get(f"/companies/{self.empty.pk}/")
        self.assertContains(response, "Not listed")
        self.assertContains(response, "No open jobs at Mango Fintech right now.")

    def test_unknown_company_shows_not_found(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get("/companies/99999/").status_code, 404)

    def test_jobs_list_links_each_company_name_to_its_page(self):
        self.client.force_login(self.user)
        response = self.client.get("/jobs/")
        self.assertContains(response, f'<a href="/companies/{self.zeta.pk}/">Zeta Health</a>', html=True, count=2)
        self.assertContains(response, f'<a href="/companies/{self.acme.pk}/">Acme Climate</a>', html=True, count=1)

    def test_companies_link_in_navigation(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("home"))
        self.assertContains(response, '<a href="/companies/">Companies</a>', html=True)


class DemoJobsSeedTests(TestCase):
    @patch.dict(os.environ, {"GRADER_ADMIN_PASSWORD": "admin-test-pass-123", "GRADER_MEMBER_PASSWORD": "member-pass-456"})
    def test_seed_adds_demo_companies_and_jobs_without_duplicates(self):
        for _ in range(3):
            call_command("seed", stdout=StringIO(), stderr=StringIO())
        self.assertEqual(Company.objects.count(), 10)
        self.assertEqual(Job.objects.count(), 20)
        self.assertTrue(all(job.apply_url.startswith("https://") and ".example.com/" in job.apply_url
                            for job in Job.objects.all()))

    @patch.dict(os.environ, {}, clear=True)
    def test_demo_jobs_load_even_without_grader_passwords(self):
        call_command("seed", stdout=StringIO(), stderr=StringIO())
        self.assertEqual(Job.objects.count(), 20)
