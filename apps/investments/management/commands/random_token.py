# your_app/management/commands/create_profiles.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.sales.models import UserProfile
from django.conf import settings
class Command(BaseCommand):
    help = 'Create user profiles for existing users'

    def handle(self, *args, **kwargs):
        users = UserProfile.objects.all()
        for user in users:
            text = user.decode()
            if text != "Omp ":
                print(f"{user.user.username}: {text}")
        self.stdout.write(self.style.SUCCESS('Successfully created user profiles for all users'))