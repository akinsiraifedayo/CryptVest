import hashlib
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction

from apps.investments.models import Wallet
from auth.views import AuthView
from .models import *
import uuid
from .forms import TopUpForm
from django.views.generic import TemplateView
from django.urls import reverse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from web_project import TemplateLayout
import requests
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import json

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
import os
from django.core.paginator import Paginator
from .utils import start_transaction, end_transaction, convert_to_nigeria_code

from django.views.decorators.csrf import csrf_exempt
from django.db import OperationalError
from rest_framework.response import Response
import time
from .utils import rate_limit_check, generate_qr_code


PURCHASE_NUMBER = os.getenv('PURCHASE_NUMBER', '')
class IndexView(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        current_user = get_object_or_404(UserProfile, user=user)
        if not (user.first_name and user.last_name and current_user.phone_number and user.email):
            messages.error(request, "Please complete your profile to gain full access to our platform.")
            return redirect("website_settings-edit_profile")
        else:
            return redirect("investments-index")
            
        # return super().dispatch(request, *args, **kwargs)

    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        current_user = get_object_or_404(UserProfile, user=self.request.user)
        context['purchase_number'] = PURCHASE_NUMBER
        context['flutterwave_enabled'] = settings.FLUTTERWAVE_ENABLED.lower()
        context['current_user'] = current_user
        website_settings = WebsiteSettings.objects.first()
        context['investment_allowed'] = website_settings.investment_allowed

        return context

class TopUpBalanceView(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        current_user = get_object_or_404(UserProfile, user=user)
        wallet = Wallet.objects.visible(current_user)

        if not wallet or not wallet.is_verified:
            messages.error(request, "Please verify your wallet to be able to deposit.")
            return redirect("website_settings-wallets")
        return super().dispatch(request, *args, **kwargs)
    
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        current_user = get_object_or_404(UserProfile, user=self.request.user)
        context['current_user'] = current_user
        context['form'] = TopUpForm()
        wallet = Wallet.objects.visible(current_user)

        context['bnb_address'] = wallet.eth_address if wallet.is_verified else ''

        # Hash the wallet address to generate a unique filename
        wallet_hash = hashlib.sha256(wallet.eth_address.encode()).hexdigest()
        file_name = f'qr_codes/{wallet_hash}_qr.png'

        # Check if the file already exists
        if not default_storage.exists(file_name):
            # If it doesn't exist, generate the QR code and save it
            qr_code_image = generate_qr_code(wallet.eth_address)
            default_storage.save(file_name, ContentFile(qr_code_image))

        # Pass the QR code image path to the template
        context["qr_code_url"] = default_storage.url(file_name)

        admin_transactions = current_user.admin_transactions.order_by('-timestamp')[:10]
        context['admin_transactions'] = admin_transactions

        online_transactions = current_user.online_transactions.order_by('-created_at')[:10]
        context['online_transactions'] = online_transactions

        website_settings = WebsiteSettings.objects.first()
        if website_settings:
            recipient_address = website_settings.deposit_address
            # wallet.approve_deposits(recipient_address)

        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        # Rate limit check
        rate_limit_passed, error_response = rate_limit_check(user)
        if not rate_limit_passed:
            messages.error(request, "You are making requests too quickly. Please wait a few seconds and try again.")
            return redirect(reverse('top_up_balance'))
        
        form = TopUpForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment_option = form.cleaned_data['payment_option']
            unique_id = str(uuid.uuid4().int)[:10]  # Unique 10-digit numeric ID
            transaction = OnlineTransaction.objects.create(
                user_profile=request.user.userprofile,
                amount=amount,
                reference=f"TXN_{request.user.id}_{unique_id}"
            )
            return redirect(reverse('process_payment', args=[transaction.reference, payment_option]))
        else:
            return self.render_to_response(self.get_context_data(form=form))



class FaqView(TemplateView):

    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        current_user = get_object_or_404(UserProfile, user=self.request.user)
        website_settings = WebsiteSettings.objects.first()
        context['support_email'] = website_settings.support_email
        context['support_phone'] = website_settings.support_phone


        return context

class TermsAndConditionsView(AuthView):

    def get(self, request):
        # Render the login page for users who are not logged in.
        return super().get(request)
