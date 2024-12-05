import json
from django.core.management.base import BaseCommand
from apps.sales.models import Sim
import os
from apps.sales.models import Sim, UserProfile
from auth.models import User, Profile
from django.utils import timezone
from datetime import timedelta, datetime
from apps.mail.utils import send_verification_email

class Command(BaseCommand):

    help = 'tests email'

    # Hardcoded path to the JSON file

    def handle(self, *args, **kwargs):
        user = User.objects.get(username='a')
        token = Profile.objects.get(user=user).email_token
        send_verification_email(user, token)
