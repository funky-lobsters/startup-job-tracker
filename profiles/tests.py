from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Profile

User = get_user_model()
PASSWORD = "s3cure-pass-123"

FILLED_IN = {
    "background": "Second-year MBA, two years in consulting.",
    "skills": "Financial modeling, customer interviews",
    "preferred_role_types": ["product", "vc_investing"],
    "preferred_locations": "New York, Remote",
    "preferred_stages": ["seed", "series_a"],
}


class ProfilePageTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(email="alice@example.com", password=PASSWORD)
        self.bob = User.objects.create_user(email="bob@example.com", password=PASSWORD)
        self.url = reverse("profiles:edit")

    def test_url_is_profile(self):
        self.assertEqual(self.url, "/profile/")

    def test_logged_out_visitor_is_sent_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next=/profile/")

    def test_form_has_all_fields(self):
        self.client.force_login(self.alice)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for name in ["background", "skills", "preferred_role_types", "preferred_locations", "preferred_stages"]:
            self.assertContains(response, f'name="{name}"')
        for label in ["Product", "VC / Investing", "Pre-seed", "Series B+"]:
            self.assertContains(response, label)

    def test_saving_stores_profile_and_shows_message(self):
        self.client.force_login(self.alice)
        response = self.client.post(self.url, FILLED_IN, follow=True)
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Profile saved")
        profile = Profile.objects.get(user=self.alice)
        self.assertEqual(profile.background, FILLED_IN["background"])
        self.assertEqual(profile.preferred_role_types, ["product", "vc_investing"])
        self.assertEqual(profile.preferred_stages, ["seed", "series_a"])
        self.assertEqual(profile.preferred_locations, "New York, Remote")

    def test_reopening_the_page_shows_what_i_saved(self):
        self.client.force_login(self.alice)
        self.client.post(self.url, FILLED_IN, follow=True)  # follow=True shows (and uses up) the message
        response = self.client.get(self.url)
        self.assertContains(response, "Second-year MBA, two years in consulting.")
        self.assertContains(response, 'value="New York, Remote"')
        self.assertContains(response, 'value="product" id="id_preferred_role_types_0" checked')
        self.assertNotContains(response, "Profile saved")  # the message shows once, right after saving

    def test_editing_updates_the_same_profile(self):
        self.client.force_login(self.alice)
        self.client.post(self.url, FILLED_IN)
        self.client.post(self.url, {**FILLED_IN, "skills": "SQL", "preferred_stages": []})
        self.assertEqual(Profile.objects.filter(user=self.alice).count(), 1)
        profile = Profile.objects.get(user=self.alice)
        self.assertEqual(profile.skills, "SQL")
        self.assertEqual(profile.preferred_stages, [])

    def test_invalid_choice_is_rejected(self):
        self.client.force_login(self.alice)
        response = self.client.post(self.url, {**FILLED_IN, "preferred_role_types": ["astronaut"]})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Profile.objects.exists())

    def test_another_user_cannot_see_my_profile(self):
        self.client.force_login(self.alice)
        self.client.post(self.url, FILLED_IN)
        self.client.force_login(self.bob)
        response = self.client.get(self.url)
        self.assertNotContains(response, "Second-year MBA")
        self.assertNotContains(response, "New York, Remote")

    def test_another_user_saving_does_not_change_my_profile(self):
        self.client.force_login(self.alice)
        self.client.post(self.url, FILLED_IN)
        self.client.force_login(self.bob)
        self.client.post(self.url, {**FILLED_IN, "background": "Bob's background"})
        self.assertEqual(Profile.objects.get(user=self.alice).background, FILLED_IN["background"])
        self.assertEqual(Profile.objects.get(user=self.bob).background, "Bob's background")

    def test_profile_link_in_navigation_when_logged_in(self):
        self.client.force_login(self.alice)
        response = self.client.get(reverse("home"))
        self.assertContains(response, '<a href="/profile/">Profile</a>', html=True)
