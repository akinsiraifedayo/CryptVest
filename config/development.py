# your_project/settings/development.py

from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "CryptVest.pythonanywhere.com"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5050",
    "https://CryptVest.pythonanywhere.com",
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
