import sys
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from dictionary.factories import SportFactory, CategoryFactory, UserFactory, TermFactory, SuggestedTermFactory, DefinitionFactory, VoteFactory
from dictionary.models import Sport, Category, Term, Definition, Vote, SuggestedTerm, TermOfTheDay


class NukeDbTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        u = UserFactory.create()
        su = UserFactory.create(is_staff=True)
        s = SportFactory.create()
        t = TermFactory.create(user=u, sport=s)
        SuggestedTermFactory.create(user=u, sport=s)
        CategoryFactory.create(sport=s)
        d = DefinitionFactory.create(user=u, term=t)
        VoteFactory.create(user=u, definition=d)

    def test_num_rows(self):
        expected_num_entries = 1

        self.assertEqual(User.objects.count(), 2)  # users will include the superuser
        self.assertEqual(Sport.objects.count(), expected_num_entries)
        self.assertEqual(Term.objects.count(), expected_num_entries)
        self.assertEqual(SuggestedTerm.objects.count(), expected_num_entries)
        self.assertEqual(Category.objects.count(), expected_num_entries)
        self.assertEqual(Definition.objects.count(), expected_num_entries)
        self.assertEqual(Vote.objects.count(), expected_num_entries)

    def test_command(self):
        total_objects = User.objects.count() + Sport.objects.count() + Term.objects.count() + Definition.objects.count() + Vote.objects.count() + Category.objects.count() + SuggestedTerm.objects.count()
        self.assertEqual(total_objects, 8)

        out = StringIO()
        sys.stdout = out
        call_command('nukedb', nuke=True, stdout=out)

        total_objects = User.objects.count() + Sport.objects.count() + Term.objects.count() + Definition.objects.count() + Vote.objects.count() + Category.objects.count() + SuggestedTerm.objects.count()
        self.assertEqual(total_objects, 1)

    def test_command_output(self):
        out = StringIO()
        sys.stdout = out
        call_command('nukedb', nuke=True, stdout=out)

        self.assertIn('Deleting 1 User row(s) (superusers spared)', out.getvalue())
        self.assertIn('Deleting 1 Profile row(s) (superusers spared)', out.getvalue())
        self.assertIn('Deleting 1 Sport row(s)', out.getvalue())
        self.assertIn('Deleting 1 Term row(s)', out.getvalue())
        self.assertIn('Deleting 1 SuggestedTerm row(s)', out.getvalue())
        self.assertIn('Deleting 1 Definition row(s)', out.getvalue())
        self.assertIn('Deleting 1 Vote row(s)', out.getvalue())

    def test_command_nukesuperusers(self):
        total_objects = User.objects.count() + Sport.objects.count() + Term.objects.count() + Definition.objects.count() + Vote.objects.count() + Category.objects.count() + SuggestedTerm.objects.count()
        self.assertEqual(total_objects, 8)

        out = StringIO()
        sys.stdout = out
        call_command('nukedb', nuke=True, nukesuperusers=True, stdout=out)

        total_objects = User.objects.count() + Sport.objects.count() + Term.objects.count() + Definition.objects.count() + Vote.objects.count() + Category.objects.count() + SuggestedTerm.objects.count()
        self.assertEqual(total_objects, 0)

    def test_command_output_nukesuperusers(self):
        out = StringIO()
        sys.stdout = out
        call_command('nukedb', nuke=True, nukesuperusers=True, stdout=out)

        self.assertIn('Deleting 2 User row(s) inc superusers', out.getvalue())
        self.assertIn('Deleting 2 Profile row(s) inc superuser profiles', out.getvalue())
        self.assertIn('Deleting 1 Sport row(s)', out.getvalue())
        self.assertIn('Deleting 1 Term row(s)', out.getvalue())
        self.assertIn('Deleting 1 SuggestedTerm row(s)', out.getvalue())
        self.assertIn('Deleting 1 Definition row(s)', out.getvalue())
        self.assertIn('Deleting 1 Vote row(s)', out.getvalue())


class SeedDb(TestCase):
    def test_command(self):
        total_objects = User.objects.count() + Sport.objects.count() + Term.objects.count() + Definition.objects.count()
        self.assertEqual(total_objects, 0)

        out = StringIO()
        sys.stdout = out
        call_command('seeddb', num_users=1, num_sports=1, num_categories=1, num_terms=1, max_num_definitions=1, stdout=out)

        total_objects = User.objects.count() + Sport.objects.count() + Term.objects.count() + Definition.objects.count()
        self.assertEqual(total_objects, 4)


class AddFutureTermsOfTheDay(TestCase):
    @classmethod
    def setUpTestData(cls):
        TermFactory.create_batch(15)

    def test_command(self):
        out = StringIO()
        sys.stdout = out
        call_command('addfuturetermsoftheday', days=7, stdout=out)

        terms_of_the_day = TermOfTheDay.objects.count()
        self.assertEqual(terms_of_the_day, 7)

    def test_only_adds_for_days_not_existing(self):
        out = StringIO()
        sys.stdout = out
        call_command('addfuturetermsoftheday', days=5)
        call_command('addfuturetermsoftheday', days=7, stdout=out)

        terms_of_the_day = TermOfTheDay.objects.count()
        self.assertEqual(terms_of_the_day, 7)

        self.assertIn(f'Added 2 new terms of the day', out.getvalue())
