import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'User {n}')
    email = factory.Sequence(lambda n: f'User{n}@sportsdictionary.com')
