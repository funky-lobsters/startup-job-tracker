import re
from unittest.mock import patch

from django.test import Client, TestCase

from .models import Visitor
from .views import source_from_referrer, team_nicknames

PAGE = "/26fd193"
CLICK = "/26fd193/click"
STATS = "/26fd193/stats"
BUTTON = re.compile(r'<button id="abtest"[^>]*>\s*(.*?)\s*</button>', re.S)


def button_text(response):
    return BUTTON.findall(response.content.decode())


class ABPageTests(TestCase):
    def test_page_is_public_and_has_exactly_one_button(self):
        response = self.client.get(PAGE)
        self.assertEqual(response.status_code, 200)
        buttons = button_text(response)
        self.assertEqual(len(buttons), 1)
        self.assertIn(buttons[0], ["kudos", "thanks"])

    def test_page_lists_team_nicknames(self):
        response = self.client.get(PAGE)
        nicknames = team_nicknames()
        self.assertTrue(nicknames)
        for nickname in nicknames:
            self.assertContains(response, nickname)

    def test_trailing_slash_redirects_without_counting(self):
        response = self.client.get(PAGE + "/")
        self.assertRedirects(response, PAGE, fetch_redirect_response=False)
        self.assertEqual(Visitor.objects.count(), 0)

    def test_each_variant_can_be_assigned(self):
        for variant in ["kudos", "thanks"]:
            with patch("abtest.views.random.choice", return_value=variant):
                response = Client().get(PAGE)
            self.assertEqual(button_text(response), [variant])

    def test_assignment_is_roughly_50_50(self):
        for _ in range(200):
            Client().get(PAGE)
        kudos = Visitor.objects.filter(variant="kudos").count()
        self.assertEqual(Visitor.objects.count(), 200)
        self.assertTrue(70 <= kudos <= 130, f"kudos={kudos} of 200 is too far from 50/50")

    def test_first_visit_counts_one_impression_and_reloads_do_not(self):
        first = button_text(self.client.get(PAGE))
        for _ in range(3):
            self.assertEqual(button_text(self.client.get(PAGE)), first)
        self.assertEqual(Visitor.objects.count(), 1)

    def test_new_visitors_each_count(self):
        Client().get(PAGE)
        Client().get(PAGE)
        self.assertEqual(Visitor.objects.count(), 2)

    def test_click_counts_once_and_redirect_keeps_variant(self):
        variant = button_text(self.client.get(PAGE))
        response = self.client.post(CLICK)
        self.assertRedirects(response, PAGE)  # follows the redirect: must not add an impression
        self.client.post(CLICK)
        visitor = Visitor.objects.get()
        self.assertIsNotNone(visitor.clicked_at)
        self.assertEqual(Visitor.objects.count(), 1)
        self.assertEqual(button_text(self.client.get(PAGE)), variant)

    def test_click_without_seeing_page_is_not_counted(self):
        response = self.client.post(CLICK)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Visitor.objects.count(), 0)

    def test_click_works_with_csrf_checks_on(self):
        client = Client(enforce_csrf_checks=True)
        client.get(PAGE)
        client.post(CLICK)
        self.assertIsNotNone(Visitor.objects.get().clicked_at)

    def test_purged_visitor_is_treated_as_new(self):
        self.client.get(PAGE)
        Visitor.objects.all().delete()
        self.client.get(PAGE)
        self.assertEqual(Visitor.objects.count(), 1)


class TrafficSourceTests(TestCase):
    """Addendum from class: record where each visitor came from (Referer header)."""

    def test_source_from_two_different_sites(self):
        Client().get(PAGE, HTTP_REFERER="https://law.yale.edu/some/page")
        Client().get(PAGE, HTTP_REFERER="https://som.yale.edu/")
        self.assertEqual(
            sorted(Visitor.objects.values_list("source", flat=True)), ["law.yale.edu", "som.yale.edu"]
        )
        self.assertEqual(Visitor.objects.get(source="law.yale.edu").referrer, "https://law.yale.edu/some/page")

    def test_missing_referrer_is_direct(self):
        self.client.get(PAGE)
        self.assertEqual(Visitor.objects.get().source, "direct")

    def test_reload_with_other_referrer_keeps_first_source(self):
        self.client.get(PAGE, HTTP_REFERER="https://law.yale.edu/")
        self.client.get(PAGE, HTTP_REFERER="https://som.yale.edu/")
        self.assertEqual(Visitor.objects.get().source, "law.yale.edu")

    def test_click_does_not_change_source(self):
        self.client.get(PAGE, HTTP_REFERER="https://law.yale.edu/")
        self.client.post(CLICK, HTTP_REFERER="https://testserver/26fd193", follow=True)
        visitor = Visitor.objects.get()
        self.assertEqual(visitor.source, "law.yale.edu")
        self.assertIsNotNone(visitor.clicked_at)

    def test_source_cleanup(self):
        self.assertEqual(source_from_referrer("https://WWW.Law.Yale.edu/x?y=1"), "law.yale.edu")
        self.assertEqual(source_from_referrer(""), "direct")
        self.assertEqual(source_from_referrer("not a url"), "direct")
        self.assertEqual(source_from_referrer("http://[bad"), "direct")


class StatsTests(TestCase):
    def make(self, variant, clicked, source="direct", n=1):
        from django.utils import timezone

        for _ in range(n):
            Visitor.objects.create(
                variant=variant, source=source, clicked_at=timezone.now() if clicked else None
            )

    def test_stats_is_public_json_with_preferred(self):
        response = self.client.get(STATS)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(data["preferred"], ["kudos", "thanks"])
        self.assertEqual(data["kudos"], {"impressions": 0, "clicks": 0})

    def test_preferred_uses_click_rate_not_click_count(self):
        # kudos: 30 clicks / 100 = 30%; thanks: 20 clicks / 40 = 50% -> thanks wins despite fewer clicks
        self.make("kudos", True, n=30)
        self.make("kudos", False, n=70)
        self.make("thanks", True, n=20)
        self.make("thanks", False, n=20)
        data = self.client.get(STATS).json()
        self.assertEqual(data["preferred"], "thanks")
        self.assertEqual(data["kudos"], {"impressions": 100, "clicks": 30})
        self.assertEqual(data["thanks"], {"impressions": 40, "clicks": 20})

    def test_stats_counts_real_page_visits(self):
        with patch("abtest.views.random.choice", return_value="kudos"):
            c = Client()
            c.get(PAGE)
            c.post(CLICK)
        with patch("abtest.views.random.choice", return_value="thanks"):
            Client().get(PAGE)
        data = self.client.get(STATS).json()
        self.assertEqual(data["preferred"], "kudos")
        self.assertEqual(data["kudos"], {"impressions": 1, "clicks": 1})
        self.assertEqual(data["thanks"], {"impressions": 1, "clicks": 0})

    def test_stats_breakdown_by_source(self):
        self.make("kudos", True, source="law.yale.edu", n=2)
        self.make("thanks", False, source="law.yale.edu")
        self.make("thanks", True, source="som.yale.edu")
        sources = self.client.get(STATS).json()["sources"]
        self.assertEqual(sources["law.yale.edu"]["kudos"], {"impressions": 2, "clicks": 2})
        self.assertEqual(sources["law.yale.edu"]["thanks"], {"impressions": 1, "clicks": 0})
        self.assertEqual(sources["som.yale.edu"]["thanks"], {"impressions": 1, "clicks": 1})
        self.assertEqual(sources["som.yale.edu"]["kudos"], {"impressions": 0, "clicks": 0})
