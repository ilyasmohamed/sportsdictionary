from datetime import date

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from dictionary.factories import SportFactory, CategoryFactory, UserFactory, TermFactory, SuggestedTermFactory, \
    DefinitionFactory, VoteFactory, TermOfTheDayFactory
from dictionary.models import SuggestedTerm, Vote


class BaseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.sport = SportFactory.create()
        cls.term = TermFactory.create()
        cls.definition = DefinitionFactory.create()
        cls.vote = VoteFactory.create()


# region Sport
class SportModelTest(BaseModelTest):

    def test_str_method(self):
        sport = SportFactory.create()
        self.assertEqual(str(sport), sport.name)

    def test_get_absolute_url(self):
        sport = SportFactory.create(name='Football')
        self.assertEquals(sport.get_absolute_url(), '/terms/football/')

    def test_slug(self):
        sport = SportFactory.create(name='American Football')
        self.assertEqual(sport.slug, 'american-football')

    def test_unique_slug(self):
        sport = SportFactory.create(name='Football')
        sport2 = SportFactory.create(name='football')
        self.assertNotEqual(sport.slug, sport2.slug)
# endregion


# region Category
class CategoryModelTest(BaseModelTest):

    def test_str_method(self):
        category = CategoryFactory.create()
        self.assertEqual(str(category), category.name)
# endregion


# region Term
class TermModelTest(BaseModelTest):

    def test_str_method(self):
        term = self.term
        self.assertEqual(str(term), f'{term.text} - {term.sport}')

    def test_get_absolute_url(self):
        sport = SportFactory.create(name='Football')
        term = TermFactory.create(text='False 9', sport=sport, user=self.user)
        self.assertEquals(term.get_absolute_url(), '/term/football/false-9')

    def test_unique_slug_if_same_sport(self):
        sport = SportFactory.create(name='Basketball')
        term = TermFactory.create(text='Rebound', sport=sport, user=self.user)
        term2 = TermFactory.create(text='rebound', sport=sport, user=self.user)
        self.assertNotEqual(term.slug, term2.slug)

    def test_non_unique_slug_if_different_sport(self):
        sport = SportFactory.create(name='Basketball')
        sport2 = SportFactory.create(name='Football')
        term = TermFactory.create(text='Rebound', sport=sport, user=self.user)
        term2 = TermFactory.create(text='Rebound', sport=sport2, user=self.user)
        self.assertEqual(term.slug, term2.slug)

    def test_term_approved_by_default(self):
        term = self.term
        self.assertTrue(term.approvedFl)

    def test_num_approved_definitions(self):
        term = TermFactory.create(text='term to test number of approved definitions', sport=self.sport, user=self.user)

        # these created definitions are approved by default
        DefinitionFactory.create(term=term, user=self.user)
        DefinitionFactory.create(term=term, user=self.user)

        # this definition has to be disapproved
        DefinitionFactory.create(term=term, user=self.user, approvedFl=False)

        self.assertEqual(term.num_approved_definitions(), 2)
# endregion


# region Suggested Term
class SuggestedTermModelTest(BaseModelTest):

    def test_is_pending_review(self):
        suggested_term = SuggestedTermFactory.create(review_status=SuggestedTerm.PENDING)
        self.assertTrue(suggested_term.is_pending_review())

    def test_is_accepted(self):
        suggested_term = SuggestedTermFactory.create(review_status=SuggestedTerm.ACCEPTED)
        self.assertTrue(suggested_term.is_accepted())

    def test_is_rejected(self):
        suggested_term = SuggestedTermFactory.create(review_status=SuggestedTerm.REJECTED)
        self.assertTrue(suggested_term.is_rejected())

    def test_term_and_definitions_create_upon_accepting_suggested_term(self):
        suggested_term = SuggestedTermFactory.create()
        suggested_term.review_status = SuggestedTerm.ACCEPTED
        suggested_term.save()

        try:
            created_term = suggested_term.term
            self.assertEqual(created_term.definitions.count(), 1)
        except ObjectDoesNotExist:
            # if we're here it means the term was not created
            self.fail('SuggestedTerm has no term')
# endregion


# region TermOfTheDay
class TermOfTheDayModelTest(BaseModelTest):

    def test_str_method(self):
        todays_term = TermOfTheDayFactory.create(day=date.today())
        self.assertEqual(str(todays_term), f'{todays_term.day} - {todays_term.term.text}')
# endregion


# region Definition
class DefinitionModelTest(BaseModelTest):

    def test_str_method(self):
        definition = self.definition
        self.assertEqual(str(definition), definition.text)

    def test_invalid_top_definition_method(self):
        definition = self.definition
        self.assertEqual(False, definition.valid_top_definition())

    def test_valid_top_definition_method(self):
        definition = self.definition
        definition.upvote(user=self.user)
        self.assertEqual(True, definition.valid_top_definition())

    def test_definition_approved_by_default(self):
        definition = self.definition
        self.assertTrue(definition.approvedFl)

    def test_num_upvotes(self):
        definition = DefinitionFactory.create(term=self.term, user=self.user)
        user2 = UserFactory.create()
        user3 = UserFactory.create()

        definition.upvote(user=self.user)
        definition.upvote(user=user2)
        definition.upvote(user=user3)

        self.assertEqual(definition.num_upvotes, 3)

    def test_num_downvotes(self):
        definition = DefinitionFactory.create(term=self.term, user=self.user)
        user2 = UserFactory.create()

        definition.downvote(user=self.user)
        definition.downvote(user=user2)

        self.assertEqual(definition.num_downvotes, 2)

    def test_net_votes(self):
        definition = DefinitionFactory.create(term=self.term, user=self.user)
        user2 = UserFactory.create()
        user3 = UserFactory.create()
        user4 = UserFactory.create()
        user5 = UserFactory.create()

        definition.upvote(user=self.user)
        definition.upvote(user=user2)
        definition.upvote(user=user3)

        definition.downvote(user=user4)
        definition.downvote(user=user5)

        self.assertEqual(definition.net_votes, 1)
        self.assertEqual(definition.num_upvotes - definition.num_downvotes,
                         definition.net_votes)
# endregion


# region Vote
class VoteModelTest(BaseModelTest):

    def test_str_method(self):
        vote = self.vote
        vote_type = 'Up' if vote.vote_type == Vote.UPVOTE else 'Down'
        definition_text = (vote.definition.text[:40] + '...') if len(vote.definition.text) > 40 else vote.definition.text
        self.assertEqual(str(vote),
                         f'{vote_type}vote by {vote.user} on definition [{definition_text}] for term [{vote.definition.term.text}]')
# endregion
