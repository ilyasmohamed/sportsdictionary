from sportsdictionary.settings.base import *

ENVIRONMENT_NAME = 'Development'
ENVIRONMENT_COLOR = '#228B22'

# Override base.py settings here
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

try:
    from sportsdictionary.settings.local import *
except:
    pass
