from django.test import TestCase
from django.urls import reverse


# region Profile
class ProfileTests(TestCase):
    def setUp(self):
        profile_url = reverse('profile')
        self.response = self.client.get(profile_url)
        self.login = reverse('login')

    def test_redirects_anonymous_users(self):
        self.assertRedirects(self.response, "%s?next=/profile/" % self.login)
# endregion