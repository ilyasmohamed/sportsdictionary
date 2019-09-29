from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.functional import SimpleLazyObject

from dictionary.models import Sport


def from_settings(request):
    return {
        'ENVIRONMENT_NAME': settings.ENVIRONMENT_NAME,
        'ENVIRONMENT_COLOR': settings.ENVIRONMENT_COLOR,
    }


def all_sports(request):
    sports = Sport.active_sports.all().order_by('name')
    return {
        'all_sports': sports,
    }


def site(request):
    return {
        'SITE': SimpleLazyObject(lambda: get_current_site(request)),
    }
