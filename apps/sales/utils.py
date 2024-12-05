from .models import UserProfile

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile, UserRequest

from datetime import timedelta
from time import sleep
from django.utils import timezone
from rest_framework.response import Response
from .models import UserRequest
# views.py
import qrcode
from django.http import HttpResponse
from django.shortcuts import render
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def generate_qr_code(wallet_address):
    # Create the QR code object
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(wallet_address)
    qr.make(fit=True)

    # Create an image in memory
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def rate_limit_check(user, seconds=5):
    now = timezone.now()
    UserRequest.objects.create(user=user)
    five_seconds_ago = now - timedelta(seconds=seconds)

    sleep(1)
    recent_requests = UserRequest.objects.filter(user=user, timestamp__gte=five_seconds_ago)
    if recent_requests.count() != 1:
        return False, Response({"error": "You are making requests too quickly. Please wait a few seconds and try again."})
    return True, None



from django.db import transaction, IntegrityError

def start_transaction(user_profile):
    try:
        with transaction.atomic():
            # Lock the row to prevent race conditions
            user_profile.refresh_from_db()
            if user_profile.transaction_in_progress:
                return False  # Transaction already in progress

            # Start the transaction
            user_profile.transaction_in_progress = True
            user_profile.save()
            return True
    except IntegrityError:
        # Handle the case where the transaction fails
        return False

def end_transaction(user_profile):
    try:
        with transaction.atomic():
            # Lock the row to prevent race conditions
            user_profile.refresh_from_db()
            if not user_profile.transaction_in_progress:
                return False  # No transaction in progress

            # End the transaction
            user_profile.transaction_in_progress = False
            user_profile.save()
            return True
    except IntegrityError:
        # Handle the case where the transaction fails
        return False

def convert_to_nigeria_code(phone_number):
    # Check if the phone number starts with "0"
    phone_number = phone_number.replace(" ", "")
    if phone_number.startswith("0"):
        # Remove the leading "0" and add "234" at the beginning
        nigeria_number = "234" + phone_number[1:]
        return nigeria_number
    elif phone_number.startswith("+"):
        return phone_number[1:]
    elif phone_number.startswith('7') or phone_number.startswith('8') or phone_number.startswith('9'):
        return "234" + phone_number[0:]
    else:
        # If the phone number doesn't start with "0", return as is
        return phone_number
