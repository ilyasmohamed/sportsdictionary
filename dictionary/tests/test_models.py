from django.test import TestCase

from dictionary.factories import SportFactory, UserFactory, TermFactory, DefinitionFactory, VoteFactory


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
        self.assertEquals(sport.get_absolute_url(), '/football/')

    def test_slug(self):
        sport = SportFactory.create(name='American Football')
        self.assertEqual(sport.slug, 'american-football')

    def test_unique_slug(self):
        sport = SportFactory.create(name='Football')
        sport2 = SportFactory.create(name='football')
        self.assertNotEqual(sport.slug, sport2.slug)
# endregion


# region Term
class TermModelTest(BaseModelTest):

    def test_str_method(self):
        term = self.term
        self.assertEqual(str(term), f'{term.text} - {term.sport}')

    def test_get_absolute_url(self):
        sport = SportFactory.create(name='Football')
        term = TermFactory.create(text='False 9', sport=sport, user=self.user)
        self.assertEquals(term.get_absolute_url(), '/football/false-9')

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


# region Definition
class DefinitionModelTest(BaseModelTest):

    def test_str_method(self):
        definition = self.definition
        self.assertEqual(str(definition), definition.text)

    def test_definition_approved_by_default(self):
        definition = self.definition
        self.assertTrue(definition.approvedFl)

    def test_num_upvotes(self):
        definition = DefinitionFactory.create(term=self.term, user=self.user)

        VoteFactory.create(definition=definition, user=self.user)
        VoteFactory.create(definition=definition, user=self.user)
        VoteFactory.create(definition=definition, user=self.user)

        self.assertEqual(definition.num_upvotes(), 3)

    def test_num_downvotes(self):
        definition = DefinitionFactory.create(term=self.term, user=self.user)

        VoteFactory.create(definition=definition, user=self.user, downvote=True)
        VoteFactory.create(definition=definition, user=self.user, downvote=True)

        self.assertEqual(definition.num_downvotes(), 2)

    def test_net_votes(self):
        definition = DefinitionFactory.create(term=self.term, user=self.user)

        VoteFactory.create(definition=definition, user=self.user)
        VoteFactory.create(definition=definition, user=self.user)
        VoteFactory.create(definition=definition, user=self.user)

        VoteFactory.create(definition=definition, user=self.user, downvote=True)
        VoteFactory.create(definition=definition, user=self.user, downvote=True)

        self.assertEqual(definition.net_votes(), 1)
# endregion


# region Vote
class VoteModelTest(BaseModelTest):

    def test_str_method(self):
        vote = self.vote
        vote_type = 'Down' if vote.downvote else 'Up'
        self.assertEqual(str(vote), f'{vote_type}vote on definition for {vote.definition.term} by {vote.user}')
# endregion