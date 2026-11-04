from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_page_loads_for_anonymous_visitor(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You are not logged in")

    def test_home_page_shows_logged_in_user(self):
        user = get_user_model().objects.create_user(email="alice@example.com", password="s3cure-pass-123")
        self.client.force_login(user)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "You are logged in as")
        self.assertContains(response, "alice@example.com")

    def test_layout_is_mobile_friendly(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'name="viewport"')
        self.assertContains(response, "pico")
