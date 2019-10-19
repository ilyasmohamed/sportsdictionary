from datetime import date
from random import randint

from django.db import models as models
from django.db.models import Count


class SportManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class ActiveSportsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class ApprovedTermManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(approvedFl=True)

    def random(self):
        count = self.get_queryset().aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


class PendingSuggestedTermManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(review_status='PEN')


class TermOfTheDayManager(models.Manager):
    def today(self):
        today = date.today()
        self.get(day=today)

    def today_and_before(self):
        return self.get_queryset().filter(day__lte=date.today()).order_by('-day')


class ApprovedDefinitionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(approvedFl=True).filter(deleteFl=False)
