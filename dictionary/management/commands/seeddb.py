import datetime
import random
import time

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from faker import Faker

from dictionary.models import Sport, Term, Definition, Vote, Category

fake = Faker()


class Command(BaseCommand):
    help = 'Seeds the db with fake data'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '-o',
            '--overwrite',
            action='store_true',
            help='overwrite existing db rows',
        )
        parser.add_argument(
            '-os',
            '--overwrite-superusers',
            action='store_true',
            help='overwrite superusers',
        )

        parser.add_argument(
            '-nu',
            '--num-users',
            type=int,
            help='the number of users to add',
        )
        parser.add_argument(
            '-ns',
            '--num-sports',
            type=int,
            help='the number of sports to add',
        )
        parser.add_argument(
            '-nc',
            '--num-categories',
            type=int,
            help='the number of categories to add for each sport',
        )
        parser.add_argument(
            '-nt',
            '--num-terms',
            type=int,
            help='the number of terms to add for each sport',
        )
        parser.add_argument(
            '-mnd',
            '--max-num-definitions',
            type=int,
            help='the maximum number of definitions to add for each term (number of definitions to add is random)',
        )

    def handle(self, *args, **options):
        num_users = 3 if not options['num_users'] else options['num_users']
        num_sports = 5 if not options['num_sports'] else options['num_sports']
        num_categories = 2 if not options['num_categories'] else options['num_categories']
        num_terms = 15 if not options['num_terms'] else options['num_terms']
        max_num_definitions = 5 if not options['max_num_definitions'] else options['max_num_definitions']

        overwrite = options['overwrite']
        overwrite_superusers = options['overwrite_superusers']

        """
            Run all seeder functions. Pass value of overwrite to all
            seeder function calls.
            Pass value of overwrite_superusers to seed users function call.
        """

        start_time = time.time()

        # run seeds
        seed_users(num_entries=num_users, overwrite=overwrite, overwrite_superusers=overwrite_superusers)
        seed_sports(num_entries=num_sports, overwrite=overwrite)
        seed_categories_for_each_sport(num_entries=num_categories, overwrite=overwrite)
        seed_terms_for_each_sport(num_entries=num_terms, overwrite=overwrite)
        seed_definitions_for_each_term(max_definitions_for_each_term=max_num_definitions, overwrite=overwrite)
        seed_votes_for_definitions(overwrite=overwrite)
        # get time

        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        print("Seeding DB took: {} minutes {} seconds".format(minutes, seconds))


def seed_users(num_entries=10, overwrite=False, overwrite_superusers=False):
    """
    Creates num_entries worth a new users
    """
    if overwrite:
        if overwrite_superusers:
            print("Overwriting all Users")
            User.objects.all().delete()
        else:
            print("Overwriting all Users except superusers")
            User.objects.filter(is_staff=False).delete()

    count = 0

    password = make_password('wy3MW5')  # use this password to login as the created users

    # first create a test user and then create the other users as necessary
    u = User(
        email="testuser@sportsdictionary.com",
        username="testuser",
        password=password
    )
    u.save()

    for _ in range(num_entries - 1):
        retry = True
        while retry:
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = first_name + last_name
            try:
                User.objects.get(username=username)
            except ObjectDoesNotExist:
                retry = False

        u = User(
            first_name=first_name,
            last_name=last_name,
            email=first_name + "." + last_name + "@faker.com",
            username=username,
            password=password
        )
        u.save()
        count += 1
        percent_complete = count / num_entries * 100
        print(
            "Adding {} new Users: {:.2f}%".format(num_entries, percent_complete),
            end='\r',
            flush=True
        )
    print()


def seed_sports(num_entries, overwrite):
    """
        Creates num_entries worth of sports
    """
    if overwrite:
        print("Overwriting Sports")
        Sport.objects.all().delete()
    count = 0
    for _ in range(num_entries):
        retry = True
        while retry:
            num_words = random.randint(1, 2)
            sport_name = ' '.join(fake.words(nb=num_words))
            try:
                Sport.objects.get(name=sport_name)
            except ObjectDoesNotExist:
                retry = False

        emoji = random.choice('🤺 🏇 ⛷️ 🏂 🏌️‍♂️ 🏌️‍♀️ 🏄‍♂️ 🏄‍♀️ 🚣‍♂️ 🚣‍♀️ 🏊‍♂️ 🏊‍♀️ ⛹️‍♂️ ⛹️‍♀️ 🏋️‍♂️ '
                              '🏋️‍♀️ 🚴‍♂️ 🚴‍♀️ 🚵‍♂️ 🚵‍♀️ 🏎️ 🏍️ 🤸 🤸‍♂️ 🤸‍♀️ 🤼 🤼‍♂️ 🤼‍♀️ 🤽 🤽‍♂️ 🤽‍♀️ 🤾 '
                              '🤾‍♂️ 🤾‍♀️ 🤹 🤹‍♂️ 🤹‍♀️ 🎖️ 🏆 🏅 🥇 🥈 🥉 ⚽ ⚾ 🏀 🏐 🏈 🏉 🎾 🎳 🏏 🏑 🏒 🏓 🏸 🥊 '
                              '🥋 🥅 ⛸️ 🎣 🎿 🛷 🥌 🎯 🎱 🧗‍♂️ 🧗‍♀️'.split(' '))
        sport = Sport(
            name=sport_name,
            slug=sport_name.replace(' ', '-'),
            active=True,
            emoji=emoji
        )
        sport.save()
        count += 1
        percent_complete = count / num_entries * 100
        print(
            "Adding {} new Sports: {:.2f}%".format(num_entries, percent_complete),
            end='\r',
            flush=True
        )
    print()


def seed_categories_for_each_sport(num_entries, overwrite):
    """
        Creates num_entries worth of categories for each sport
    """
    if overwrite:
        print("Overwriting Categories")
        Category.objects.all().delete()

    count = 0

    sports = Sport.objects.all()
    sports_count = len(sports)
    total_categories_to_add = sports_count * num_entries

    for sport in sports:
        for _ in range(num_entries):
            retry = True
            while retry:
                num_words = random.randint(1, 2)
                category_name = ' '.join(fake.words(nb=num_words))
                try:
                    Category.objects.get(name=category_name, sport=sport)
                except ObjectDoesNotExist:
                    retry = False

            category = Category(
                name=category_name,
                sport=sport
            )
            category.save()
            count += 1
        percent_complete = count / total_categories_to_add * 100
        print(
            "Adding {} new Categories: {:.2f}%".format(total_categories_to_add, percent_complete),
            end='\r',
            flush=True
        )
    print()


def seed_terms_for_each_sport(num_entries, overwrite):
    """
        Creates num_entries worth of terms
    """
    if overwrite:
        print("Overwriting Terms")
        Term.objects.all().delete()
    count = 0

    sports = Sport.objects.all()
    sports_count = len(sports)
    total_terms_to_add = sports_count * num_entries

    for sport in sports:
        for _ in range(num_entries):
            retry = True
            while retry:
                num_words = random.randint(3, 5)
                term_text = ' '.join(fake.words(nb=num_words))
                try:
                    Term.objects.get(text=term_text, sport=sport)
                except ObjectDoesNotExist:
                    retry = False

            term = Term(
                text=term_text,
                slug=term_text.replace(' ', '-'),
                approvedFl=True,
                created=datetime.datetime.now(),
                last_updated=datetime.datetime.now(),
                sport=sport
            )
            term.save()

            categories = Category.objects.filter(sport=sport)
            categories_count = len(categories)
            category = categories[random.randint(0, categories_count - 1)]  # get random category
            term.categories.add(category)

            count += 1
        percent_complete = count / total_terms_to_add * 100
        print(
            "Adding {} new Terms: {:.2f}%".format(total_terms_to_add, percent_complete),
            end='\r',
            flush=True
        )
    print()


def seed_definitions_for_each_term(max_definitions_for_each_term, overwrite):
    """
        Creates definitions for each term (max of max_num_defs_for_each_Term)
    """
    max_definitions_for_each_term = 1 if max_definitions_for_each_term < 1 else max_definitions_for_each_term

    if overwrite:
        print("Overwriting Definitions")
        Definition.objects.all().delete()
    count = 0

    terms = Term.objects.all()

    for term in terms:
        num_of_definitions_to_add = random.randint(1, max_definitions_for_each_term)
        for _ in range(num_of_definitions_to_add):
            num_sentences = random.randint(1, 3)
            definition_text = ' '.join(fake.sentences(nb=num_sentences))

            users = User.objects.filter(is_staff=False)
            users_count = len(users)
            user = users[random.randint(0, users_count - 1)]  # get random user
            definition = Definition(
                text=definition_text,
                approvedFl=True,
                created=datetime.datetime.now(),
                last_updated=datetime.datetime.now(),
                term=term,
                user=user
            )
            definition.save()
            count += 1
    print("Added {} new Definitions".format(count))


def seed_votes_for_definitions(overwrite):
    """
        Creates a vote for each definition
    """

    if overwrite:
        print("Overwriting Votes")
        Vote.objects.all().delete()

    count = 0

    definitions = Definition.objects.all()
    users = User.objects.filter(is_staff=False)

    for user in users:
        for definition in definitions:
            if definition.user == user:
                continue

            should_vote = random.choice(['y', 'n'])
            if should_vote == 'y':
                vote_type = random.choice([-1, 1])
                if vote_type == -1:
                    definition.downvote(user=user)
                else:
                    definition.upvote(user=user)
                count += 1
    print("Added {} new Votes".format(count))
