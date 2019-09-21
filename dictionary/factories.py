import factory
from factory.django import DjangoModelFactory

from accounts.factories import UserFactory
from dictionary.models import Sport, Category, SuggestedTerm, Term, Definition, Vote


class SportFactory(DjangoModelFactory):
    class Meta:
        model = Sport

    name = factory.Sequence(lambda n: f'Sport {n}')
    active = True


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    sport = factory.SubFactory(SportFactory)
    name = factory.Sequence(lambda n: f'Category {n}')


class TermFactory(DjangoModelFactory):
    class Meta:
        model = Term

    sport = factory.SubFactory(SportFactory)
    user = factory.SubFactory(UserFactory)
    text = factory.Sequence(lambda n: f'Term text {n}')


class SuggestedTermFactory(DjangoModelFactory):
    class Meta:
        model = SuggestedTerm

    sport = factory.SubFactory(SportFactory)
    user = factory.SubFactory(UserFactory)
    text = factory.Sequence(lambda n: f'Suggested Term text {n}')
    example_usage = factory.Sequence(lambda n: f'Example usage for suggested term {n}')
    review_status = SuggestedTerm.PENDING


class DefinitionFactory(DjangoModelFactory):
    class Meta:
        model = Definition

    term = factory.SubFactory(TermFactory)
    user = factory.SubFactory(UserFactory)
    text = factory.Sequence(lambda n: f'Definition {n}')
    example_usage = factory.Sequence(lambda n: f'Example usage for definition {n}')


class VoteFactory(DjangoModelFactory):
    class Meta:
        model = Vote

    definition = factory.SubFactory(DefinitionFactory)
    user = factory.SubFactory(UserFactory)
    vote_type = Vote.UPVOTE
