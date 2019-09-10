from django.test import TestCase

from dictionary.factories import SportFactory
from dictionary.models import Sport


class AllSports(TestCase):
    @classmethod
    def setUpTestData(cls):
        SportFactory.create_batch(50)
        SportFactory.create(active=False)

    def test_total_num_sports(self):
        sports = Sport.objects.all()
        self.assertEqual(51, sports.count())

    def test_all_sports_in_context(self):
        response = self.client.get('/')
        self.assertTrue('all_sports' in response.context)

    def test_all_sports_contains_only_active_sports(self):
        response = self.client.get('/')
        all_sports = response.context['all_sports']
        self.assertEqual(len(all_sports), 50)
