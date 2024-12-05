from django.conf import settings

if settings.DEBUG:
    print("Running in development mode")
else:
    print("Running in production mode")
