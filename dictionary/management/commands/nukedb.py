from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from dictionary.models import Sport, Term, Definition, Vote, Category, Profile, SuggestedTerm


class Command(BaseCommand):
    help = 'Deletes all the db rows'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--nuke',
            action='store_true',
            help='delete all db rows',
        )
        parser.add_argument(
            '--nukesuperusers',
            action='store_true',
            help='also deletes superuser rows if this flag is specified',
        )

    def handle(self, *args, **options):
        if options['nuke']:
            votes = Vote.objects.all()
            print(f'Deleting {len(votes)} Vote row(s)')
            votes.delete()

            definitions = Definition.objects.all()
            print(f'Deleting {len(definitions)} Definition row(s)')
            definitions.delete()

            categories = Category.objects.all()
            print(f'Deleting {len(categories)} Category row(s)')
            categories.delete()

            suggested_terms = SuggestedTerm.objects.all()
            print(f'Deleting {len(suggested_terms)} SuggestedTerm row(s)')
            suggested_terms.delete()

            terms = Term.objects.all()
            print(f'Deleting {len(terms)} Term row(s)')
            terms.delete()

            sports = Sport.objects.all()
            print(f'Deleting {len(sports)} Sport row(s)')
            sports.delete()

            if options['nukesuperusers']:
                profiles = Profile.objects.all()
                print(f'Deleting {len(profiles)} Profile row(s) inc superuser profiles')
                profiles.delete()

                users = User.objects.all()
                print(f'Deleting {len(users)} User row(s) inc superusers')
                users.delete()
            else:
                profiles = Profile.objects.filter(user__is_staff=False)
                print(f'Deleting {len(profiles)} Profile row(s) (superusers spared)')
                profiles.delete()

                users = User.objects.filter(is_staff=False)
                print(f'Deleting {len(users)} User row(s) (superusers spared)')
                users.delete()

        else:
            print('Didn\'t delete any rows as the --nuke option was not specified')
