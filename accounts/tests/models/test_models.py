from django.test import TestCase

from accounts.models import Profile
from accounts.factories import UserFactory


# region Profile
class ProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()

    def test_profile_is_created(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile, self.user.profile)
# endregion
