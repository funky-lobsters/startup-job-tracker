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
        # Session + user + one jobs query that also loads companies (no extra query per job).
        with self.assertNumQueries(3):
            self.client.get(self.url)


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

    def test_company_name_is_plain_text_until_company_pages_exist(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, '<p class="company-name">Lanternfish Labs</p>', html=True)

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
