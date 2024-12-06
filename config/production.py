from .base import *
import os

SUBDOMAIN_NAME = os.getenv('SUBDOMAIN_NAME', '')

DEBUG = True

ALLOWED_HOSTS = [f'{SUBDOMAIN_NAME}']

CSRF_TRUSTED_ORIGINS = [
    f"https://{SUBDOMAIN_NAME}",
]

# Email Settings
# ------------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_PORT = 587
EMAIL_USE_TLS = True


DB_NAME = os.getenv('DB_NAME', '')
DB_USER = os.getenv('DB_USER', '')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': DB_NAME,
#         'USER': DB_USER,
#         'PASSWORD': DB_PASSWORD,
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_DOMAIN = os.getenv('CSRF_COOKIE_DOMAIN', '')
