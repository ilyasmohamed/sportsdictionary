from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from dictionary.models import Term, Definition, Sport, Vote


def create_django_contrib_auth_models_user(**kwargs):
    defaults = {"username": "username", "email": "username@tempurl.com"}
    defaults.update(**kwargs)
    return User.objects.create(**defaults)


# def create_django_contrib_auth_models_group(**kwargs):
#     defaults = {"name": "group"}
#     defaults.update(**kwargs)
#     return Group.objects.create(**defaults)
#
#
# def create_django_contrib_contenttypes_models_contenttype(**kwargs):
#     defaults = {}
#     defaults.update(**kwargs)
#     return ContentType.objects.create(**defaults)


def create_sport(**kwargs):
    defaults = {"name": "name"}
    defaults.update(**kwargs)
    return Sport.objects.create(**defaults)


def create_term(**kwargs):
    defaults = {"text": "text"}
    defaults.update(**kwargs)
    if "sport" not in defaults:
        defaults["sport"] = create_sport()
    if "user" not in defaults:
        defaults["user"] = create_django_contrib_auth_models_user()
    return Term.objects.create(**defaults)


def create_definition(**kwargs):
    defaults = {"text": "text", "approvedFl": True}
    defaults.update(**kwargs)
    if "term" not in defaults:
        defaults["term"] = create_term()
    if "user" not in defaults:
        defaults["user"] = create_django_contrib_auth_models_user()
    return Definition.objects.create(**defaults)


def create_upvote(**kwargs):
    kwargs.update({"downvote": False})
    return create_vote(**kwargs)


def create_downvote(**kwargs):
    kwargs.update({"downvote": True})
    return create_vote(**kwargs)


def create_vote(**kwargs):
    defaults = {"downvote": False}
    defaults.update(**kwargs)
    if "user" not in defaults:
        defaults["user"] = create_django_contrib_auth_models_user()
    if "definition" not in defaults:
        defaults["definition"] = create_definition()
    return Vote.objects.create(**defaults)


class BaseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_django_contrib_auth_models_user()
        cls.sport = create_sport()
        cls.term = create_term(sport=cls.sport, user=cls.user)
        cls.definition = create_definition(term=cls.term, user=cls.user)
        cls.vote = create_vote(definition=cls.definition, user=cls.user)


# region Sport
class SportModelTest(BaseModelTest):

    def test_str_method(self):
        sport = self.sport
        self.assertEqual(str(sport), sport.name)

    def test_get_absolute_url(self):
        sport = create_sport(name='Football')
        self.assertEquals(sport.get_absolute_url(), '/football/')

    def test_slug(self):
        sport = create_sport(name='American Football')
        self.assertEqual(sport.slug, 'american-football')

    def test_unique_slug(self):
        sport = create_sport(name='Football')
        sport2 = create_sport(name='football')
        self.assertNotEqual(sport.slug, sport2.slug)
# endregion


# region Term
class TermModelTest(BaseModelTest):

    def test_str_method(self):
        term = self.term
        self.assertEqual(str(term), f'{term.text} - {term.sport}')

    def test_get_absolute_url(self):
        sport = create_sport(name='Football')
        term = create_term(text='False 9', sport=sport, user=self.user)
        self.assertEquals(term.get_absolute_url(), '/football/false-9')

    def test_unique_slug_if_same_sport(self):
        sport = create_sport(name='Basketball')
        term = create_term(text='Rebound', sport=sport, user=self.user)
        term2 = create_term(text='rebound', sport=sport, user=self.user)
        self.assertNotEqual(term.slug, term2.slug)

    def test_non_unique_slug_if_different_sport(self):
        sport = create_sport(name='Basketball')
        sport2 = create_sport(name='Football')
        term = create_term(text='Rebound', sport=sport, user=self.user)
        term2 = create_term(text='Rebound', sport=sport2, user=self.user)
        self.assertEqual(term.slug, term2.slug)

    def test_term_approved_by_default(self):
        term = self.term
        self.assertTrue(term.approvedFl)

    def test_num_approved_definitions(self):
        term = create_term(text='term to test number of approved definitions', sport=self.sport, user=self.user)

        # these created definitions are approved by default
        create_definition(term=term, user=self.user)
        create_definition(term=term, user=self.user)

        # this definition has to be disapproved
        create_definition(term=term, user=self.user, approvedFl=False)

        self.assertEqual(term.num_approved_definitions(), 2)
# endregion


# region Definition
class DefinitionModelTest(BaseModelTest):

    def test_str_method(self):
        definition = self.definition
        self.assertEqual(str(definition), definition.text)

    def test_definition_approved_by_default(self):
        definition = self.definition
        self.assertTrue(definition.approvedFl)

    def test_num_upvotes(self):
        definition = create_definition(term=self.term, user=self.user)

        create_upvote(definition=definition, user=self.user)
        create_upvote(definition=definition, user=self.user)
        create_upvote(definition=definition, user=self.user)

        self.assertEqual(definition.num_upvotes(), 3)

    def test_num_downvotes(self):
        definition = create_definition(term=self.term, user=self.user)

        create_downvote(definition=definition, user=self.user)
        create_downvote(definition=definition, user=self.user)

        self.assertEqual(definition.num_downvotes(), 2)

    def test_net_votes(self):
        definition = create_definition(term=self.term, user=self.user)

        create_upvote(definition=definition, user=self.user)
        create_upvote(definition=definition, user=self.user)
        create_upvote(definition=definition, user=self.user)

        create_downvote(definition=definition, user=self.user)
        create_downvote(definition=definition, user=self.user)

        self.assertEqual(definition.net_votes(), 1)
# endregion


# region Vote
class VoteModelTest(BaseModelTest):

    def test_str_method(self):
        vote = self.vote
        vote_type = 'Down' if vote.downvote else 'Up'
        self.assertEqual(str(vote), f'{vote_type}vote on definition for {vote.definition.term} by {vote.user}')
# endregion
