from django.test import TestCase

from dictionary.templatetags.custom_urlize import custom_urlize
from dictionary.factories import SportFactory, UserFactory, TermFactory, SuggestedTermFactory, DefinitionFactory, VoteFactory


class BaseTagsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.sport = SportFactory.create()
        cls.term = TermFactory.create()
        cls.definition = DefinitionFactory.create()
        cls.vote = VoteFactory.create()


class CustomUrlizeTest(BaseTagsTest):

    def test_valid_internal_link_same_sport_no_label(self):
        result = custom_urlize(f'[[{self.term.slug}]]', self.term.sport)
        self.assertEqual(result, f'<a href="{self.term.get_absolute_url()}" class="term-link-in-definition">{self.term.text.lower()}</a>')

    def test_valid_internal_link_same_sport_with_label(self):
        label = ' a test label '
        result = custom_urlize(f'[[{self.term.slug}|{label}]]', self.term.sport)
        self.assertEqual(result, f'<a href="{self.term.get_absolute_url()}" class="term-link-in-definition">{label.strip()}</a>')

    def test_valid_internal_link_different_sport_no_label(self):
        different_sport = SportFactory.create(name='Different sport')
        term = TermFactory.create(sport=different_sport, text='Text')

        result = custom_urlize(f'[[{term.slug}]]', different_sport)
        self.assertEqual(result, f'<a href="{term.get_absolute_url()}" class="term-link-in-definition">{term.text.lower()}</a>')

    def test_valid_internal_link_different_sport_with_label(self):
        different_sport = SportFactory.create(name='Different sport')
        term = TermFactory.create(sport=different_sport, text='Text')
        label = ' a test label for my link'
        result = custom_urlize(f'[[{term.slug}|{label}]]', different_sport)

        self.assertEqual(result, f'<a href="{term.get_absolute_url()}" class="term-link-in-definition">{label.strip()}</a>')

    def test_invalid_internal_link_no_label(self):
        term_slug = 'a-made-up-slug'
        result = custom_urlize(f'[[{term_slug}]]', self.term.sport)
        self.assertEqual(result, f'<a href="#" class="bad-link">{term_slug}</a>')

    def test_invalid_internal_link_with_label(self):
        term_slug = 'a-made-up-slug'
        label = 'a label'
        result = custom_urlize(f'[[{term_slug}|{label}]]', self.term.sport)
        self.assertEqual(result, f'<a href="#" class="bad-link">{label.strip()}</a>')
