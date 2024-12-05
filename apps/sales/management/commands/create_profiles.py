# your_app/management/commands/create_profiles.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.sales.models import UserProfile

class Command(BaseCommand):
    help = 'Create user profiles for existing users'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            UserProfile.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS('Successfully created user profiles for all users'))
