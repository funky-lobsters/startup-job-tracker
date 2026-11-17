"""Tests for "Recommended for you". The real AI is never called: OpenRouter is always mocked."""

import json
import urllib.error
from datetime import date
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from jobs.models import Company, Job
from profiles.models import Profile

from .ai import AIError, build_messages, call_openrouter, parse_recommendations

User = get_user_model()
PASSWORD = "s3cure-pass-123"
FAKE_KEY = "sk-or-v1-test-key-not-real"
CALL_AI = "recommendations.ai.call_openrouter"


def ai_reply(*pairs):
    """What the model would answer: JSON with job ids and reasons."""
    return json.dumps({"recommendations": [{"job_id": job_id, "reason": reason} for job_id, reason in pairs]})


class RecommendationsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="seeker@example.com", password=PASSWORD)
        self.url = reverse("recommendations:list")
        seed = Company.objects.create(name="Lanternfish Labs", stage=Company.Stage.SEED)
        fund = Company.objects.create(name="Harbor Ventures", stage=Company.Stage.SERIES_A)
        self.pm_job = Job.objects.create(
            company=seed, title="Product Manager", location="New York, NY", role_type=Job.RoleType.PRODUCT,
            posted_date=date(2026, 11, 10), apply_url="https://lanternfish-labs.example.com/careers/pm",
        )
        self.vc_job = Job.objects.create(
            company=fund, title="Investment Associate", location="Remote", role_type=Job.RoleType.VC_INVESTING,
            posted_date=date(2026, 11, 9), apply_url="https://harbor-ventures.example.com/jobs/associate",
        )

    def make_profile(self, user=None):
        return Profile.objects.create(
            user=user or self.user,
            background="Second-year MBA, two years in consulting.",
            skills="Financial modeling, customer interviews",
            preferred_role_types=["product", "vc_investing"],
            preferred_locations="New York, Remote",
            preferred_stages=["seed"],
        )


class RecommendationsPageTests(RecommendationsTestCase):
    def test_url_is_recommendations(self):
        self.assertEqual(self.url, "/recommendations/")

    def test_logged_out_visitor_is_sent_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next=/recommendations/")

    @patch(CALL_AI)
    def test_shows_recommended_jobs_with_reasons_and_links(self, fake_ai):
        self.make_profile()
        fake_ai.return_value = ai_reply(
            (self.vc_job.id, "You know financial modeling, which this fund needs."),
            (self.pm_job.id, "You did customer interviews in consulting."),
        )
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        fake_ai.assert_called_once()
        self.assertContains(response, "Investment Associate")
        self.assertContains(response, "You know financial modeling, which this fund needs.")
        self.assertContains(response, "Product Manager")
        self.assertContains(response, 'href="https://harbor-ventures.example.com/jobs/associate"')
        self.assertContains(response, 'target="_blank"')
        # Best fit first, in the order the AI gave.
        html = response.content.decode()
        self.assertLess(html.index("Investment Associate"), html.index("Product Manager"))

    @patch(CALL_AI)
    def test_each_job_links_to_its_detail_page_and_apply_opens_new_tab(self, fake_ai):
        self.make_profile()
        fake_ai.return_value = ai_reply((self.pm_job.id, "You did customer interviews in consulting."))
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertContains(
            response, f'<a href="/jobs/{self.pm_job.id}/">Product Manager</a>', html=True,
        )
        self.assertContains(
            response,
            '<a href="https://lanternfish-labs.example.com/careers/pm" target="_blank" '
            'rel="noopener noreferrer" role="button">Apply</a>',
            html=True,
        )

    @patch(CALL_AI)
    def test_profile_and_jobs_are_sent_to_the_ai(self, fake_ai):
        self.make_profile()
        fake_ai.return_value = ai_reply()
        self.client.force_login(self.user)
        self.client.get(self.url)

        messages = fake_ai.call_args.args[0]
        prompt = messages[-1]["content"]
        self.assertIn("two years in consulting", prompt)
        self.assertIn("VC / Investing", prompt)
        self.assertIn(f"id {self.pm_job.id}: Product Manager at Lanternfish Labs", prompt)

    @patch(CALL_AI)
    def test_no_profile_asks_to_fill_it_in(self, fake_ai):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertContains(response, 'id="needs-profile"')
        self.assertContains(response, f'href="{reverse("profiles:edit")}"')
        fake_ai.assert_not_called()  # no point asking the AI (or paying for it)

    @patch(CALL_AI)
    def test_empty_profile_also_asks_to_fill_it_in(self, fake_ai):
        Profile.objects.create(user=self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertContains(response, 'id="needs-profile"')
        fake_ai.assert_not_called()

    @patch(CALL_AI)
    def test_no_jobs_says_so_without_calling_the_ai(self, fake_ai):
        self.make_profile()
        Job.objects.all().delete()
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertContains(response, 'id="no-jobs"')
        fake_ai.assert_not_called()

    @patch(CALL_AI, side_effect=AIError("OpenRouter call failed"))
    def test_ai_error_shows_friendly_message(self, fake_ai):
        self.make_profile()
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="ai-error"')
        self.assertContains(response, "get recommendations right now")

    @patch(CALL_AI, return_value="this is not JSON")
    def test_nonsense_reply_shows_friendly_message(self, fake_ai):
        self.make_profile()
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="ai-error"')

    @patch(CALL_AI)
    def test_no_good_match_says_so(self, fake_ai):
        self.make_profile()
        fake_ai.return_value = ai_reply()
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertContains(response, 'id="no-matches"')

    @override_settings(OPENROUTER_API_KEY="")
    def test_missing_api_key_shows_friendly_message(self):
        self.make_profile()
        self.client.force_login(self.user)
        with patch("urllib.request.urlopen") as fake_urlopen:
            response = self.client.get(self.url)
            fake_urlopen.assert_not_called()
        self.assertContains(response, 'id="ai-error"')

    @patch(CALL_AI)
    def test_uses_my_own_profile_only(self, fake_ai):
        other = User.objects.create_user(email="other@example.com", password=PASSWORD)
        self.make_profile(user=other)  # someone else has a profile, I don't
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertContains(response, 'id="needs-profile"')
        fake_ai.assert_not_called()

    def test_nav_has_for_you_link(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("jobs:list"))
        self.assertContains(response, f'href="{self.url}"')


class ParseRecommendationsTests(RecommendationsTestCase):
    """The AI can only point at jobs that really exist; everything else is dropped."""

    def test_unknown_job_ids_are_dropped(self):
        jobs = [self.pm_job, self.vc_job]
        results = parse_recommendations(ai_reply((99999, "Made-up job"), (self.pm_job.id, "Good fit.")), jobs)
        self.assertEqual(results, [(self.pm_job, "Good fit.")])

    def test_duplicates_and_empty_reasons_are_dropped(self):
        jobs = [self.pm_job, self.vc_job]
        reply = ai_reply((self.pm_job.id, "First."), (self.pm_job.id, "Again."), (self.vc_job.id, "  "))
        self.assertEqual(parse_recommendations(reply, jobs), [(self.pm_job, "First.")])

    def test_at_most_five(self):
        company = self.pm_job.company
        jobs = [
            Job.objects.create(company=company, title=f"Role {n}", location="Remote", posted_date=date(2026, 11, 1),
                               apply_url=f"https://example.com/{n}")
            for n in range(8)
        ]
        reply = ai_reply(*[(job.id, f"Reason {job.id}.") for job in jobs])
        self.assertEqual(len(parse_recommendations(reply, jobs)), 5)

    def test_wrong_shape_raises_ai_error(self):
        for reply in ["not json", "[]", '{"recommendations": "nope"}', '{"something_else": []}']:
            with self.subTest(reply=reply), self.assertRaises(AIError):
                parse_recommendations(reply, [self.pm_job])

    def test_long_reasons_are_cut(self):
        results = parse_recommendations(ai_reply((self.pm_job.id, "x" * 1000)), [self.pm_job])
        self.assertEqual(len(results[0][1]), 300)


@override_settings(OPENROUTER_API_KEY=FAKE_KEY, OPENROUTER_MODEL="test/model", OPENROUTER_TIMEOUT_SECONDS=7)
class CallOpenRouterTests(RecommendationsTestCase):
    """The HTTP call itself, with the network replaced by a fake (urlopen is mocked)."""

    def fake_response(self, body):
        response = MagicMock()
        response.read.return_value = json.dumps(body).encode()
        response.__enter__.return_value = response
        return response

    @patch("urllib.request.urlopen")
    def test_sends_key_model_and_structured_output_request(self, fake_urlopen):
        fake_urlopen.return_value = self.fake_response({"choices": [{"message": {"content": ai_reply()}}]})
        reply = call_openrouter(build_messages(self.make_profile(), [self.pm_job]))

        self.assertEqual(reply, ai_reply())
        request = fake_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(request.get_header("Authorization"), f"Bearer {FAKE_KEY}")
        payload = json.loads(request.data)
        self.assertEqual(payload["model"], "test/model")
        self.assertEqual(payload["response_format"]["type"], "json_schema")
        self.assertEqual(fake_urlopen.call_args.kwargs["timeout"], 7)

    @patch("urllib.request.urlopen", side_effect=TimeoutError("timed out"))
    def test_timeout_raises_ai_error(self, fake_urlopen):
        with self.assertRaises(AIError):
            call_openrouter([{"role": "user", "content": "hi"}])

    @patch("urllib.request.urlopen")
    def test_http_error_raises_ai_error(self, fake_urlopen):
        fake_urlopen.side_effect = urllib.error.HTTPError(
            "https://openrouter.ai/api/v1/chat/completions", 401, "Unauthorized", {}, None
        )
        with self.assertRaises(AIError):
            call_openrouter([{"role": "user", "content": "hi"}])

    @patch("urllib.request.urlopen")
    def test_unexpected_response_raises_ai_error(self, fake_urlopen):
        fake_urlopen.return_value = self.fake_response({"error": {"message": "model not found"}})
        with self.assertRaises(AIError):
            call_openrouter([{"role": "user", "content": "hi"}])

    @patch("urllib.request.urlopen")
    def test_api_key_is_not_logged(self, fake_urlopen):
        fake_urlopen.side_effect = urllib.error.URLError("network down")
        with self.assertLogs("recommendations.ai", level="WARNING") as logs, self.assertRaises(AIError):
            call_openrouter([{"role": "user", "content": "hi"}])
        self.assertNotIn(FAKE_KEY, "\n".join(logs.output))
