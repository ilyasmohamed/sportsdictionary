from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from dictionary.models import Term, Definition, Sport
from dictionary.factories import SportFactory, UserFactory, TermFactory, DefinitionFactory, VoteFactory


class IndexView(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 200 Terms
        num_terms = 200

        TermFactory.create_batch(num_terms)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dictionary/index.html')

    def test_pagination_is_x(self):
        x = 20

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['terms']), x)

    def test_pagination_page_number(self):
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].number, 2)

    def test_paginator_hold_all_terms(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['paginator'].count, 200)


class SportView(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 100 Terms in a single belonging to a single sport
        num_terms = 100
        cls.sport = SportFactory.create()

        TermFactory.create_batch(num_terms, sport=cls.sport)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/terms/' + self.sport.slug + '/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('sport_index', kwargs={'sport_slug': self.sport.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('sport_index', kwargs={'sport_slug': self.sport.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dictionary/sport_index.html')

    def test_pagination_is_x(self):
        x = 20

        response = self.client.get(reverse('sport_index', kwargs={'sport_slug': self.sport.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['terms']), x)

    def test_pagination_page_number(self):
        response = self.client.get(reverse('sport_index', kwargs={'sport_slug': self.sport.slug})+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].number, 2)

    def test_paginator_holds_all_terms_from_sport(self):
        response = self.client.get(reverse('sport_index', kwargs={'sport_slug': self.sport.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['paginator'].count, 100)

    def test_paginator_only_holds_terms_from_sport(self):
        another_sport = SportFactory.create(name='Another Sport')
        TermFactory.create(
            sport=another_sport,
            text='Term in another sport'
        )

        response = self.client.get(reverse('sport_index', kwargs={'sport_slug': self.sport.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['paginator'].count, 100)

        # verify other term exists (total num of terms should = 101)
        terms = Term.objects.all()
        self.assertEqual(terms.count(), 101)


class TermDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sport, a term belonging to that sport & 10 definitions for that term
        sport = SportFactory.create(name='Sport')
        cls.term = TermFactory.create(
            sport=sport,
            text='Term for sport'
        )

        cls.user = UserFactory.create(username='username')
        DefinitionFactory.create_batch(
            10,
            term=cls.term,
            user=cls.user
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/term/' + self.term.sport.slug + '/' + self.term.slug)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('term_detail',
                                           kwargs={'sport_slug': self.term.sport.slug,
                                                   'term_slug': self.term.slug}
                                           ))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('term_detail',
                                           kwargs={'sport_slug': self.term.sport.slug,
                                                   'term_slug': self.term.slug}
                                           ))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dictionary/term_detail.html')

    def test_view_has_correct_number_of_definitions(self):
        response = self.client.get(reverse('term_detail',
                                           kwargs={'sport_slug': self.term.sport.slug,
                                                   'term_slug': self.term.slug}
                                           ))

        definitions_for_term = response.context['definitions']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(definitions_for_term.count(), 10)

    def test_view_only_includes_approved_definitions(self):
        Definition.objects.create(
            term=self.term,
            user=self.user,
            text='An unapproved definitions',
            approvedFl=False
        )

        definitions_for_term = Definition.objects.filter(term=self.term)

        response = self.client.get(reverse('term_detail',
                                           kwargs={'sport_slug': self.term.sport.slug,
                                                   'term_slug': self.term.slug}
                                           ))

        self.assertEqual(response.context['definitions'].count(), 10)
        self.assertEqual(definitions_for_term.count(), 11)
