from django.conf import settings
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
