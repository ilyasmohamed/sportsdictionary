from datetime import date

import pandas as pd
from django.core.management.base import BaseCommand

from dictionary.models import TermOfTheDay, Term


class Command(BaseCommand):
    help = 'Adds future terms of the day'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='the number of days in the future to add terms of the day for',
        )

    def handle(self, *args, **options):
        days_in_future = options['days']
        today = date.today()
        dates_to_add = pd.date_range(start=today, periods=days_in_future).to_list()

        num_totd_added = 0

        for d in dates_to_add:
            day = d.date()
            try:
                TermOfTheDay.objects.get(day=day)
                continue
            except TermOfTheDay.DoesNotExist:
                # add a term for this day as it doesn't already exist
                random_term = Term.approved_terms.random()
                totd = TermOfTheDay(day=day, term=random_term)
                totd.save()
                num_totd_added += 1
                print(f'Added new term of the day for date {day}')

        print(f'Added {num_totd_added} new terms of the day')
