import re
import uuid
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from apps.investments.utils import sufficent_withdrawal_fees
from apps.sales.models import WebhookLog
from apps.sales.utils import rate_limit_check
from .models import *
from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.conf import settings
from apps.website_settings.models import InvestmentSetting, WebsiteSettings
from .forms import InvestmentForm, InvestmentWithdrawalForm
from django.utils.safestring import mark_safe

from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
import datetime
# Create your views here.

class IndexView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        current_user = get_object_or_404(UserProfile, user=self.request.user)
        context['current_user'] = current_user

        # pagination start
        per_page = self.request.GET.get('per_page') if self.request.GET.get('per_page') else 10
        investments = Investment.objects.filter(user_profile=current_user).order_by('-end_time')
        paginator = Paginator(investments, per_page)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        context['per_page'] = per_page
        # pagination end

        return context


@csrf_exempt
@api_view(['GET'])
def get_wallets_to_refresh(request, signature):
    current_time = datetime.datetime.now()
    secret = settings.REFRESH_SECRET
    # signature = request.headers.get('refresh_secret')
    

    if not signature:
        WebhookLog.objects.create(
            event_type='unknown',
            payload={},
            status='invalid signature header'
        )
        return JsonResponse({"status_code": f'HEY {signature}'}, status=411)

    if signature != secret:
        WebhookLog.objects.create(
            event_type='unknown',
            payload={},
            status='invalid signature'
        )
        return JsonResponse({"status_code": 511}, status=511)
    

    website_settings = WebsiteSettings.objects.first()
    deposit_address = website_settings.deposit_address

    # ten minute task
    # if current_time.minute % 10 == 0:
    main_wallets = Wallet.objects.filter(is_visible=True, is_verified=True)
    for wallet in main_wallets:
        wallet.approve_deposits(deposit_address)

    # hourly task
    if current_time.minute < 2:
        main_wallets = Wallet.objects.filter(is_visible=True, is_verified=True)
        for wallet in main_wallets:
            wallet.update_balances()

    if current_time.hour == 0:
        investments = Investment.objects.filter(is_active=True)
        for investment in investments:
            investment.give_roi()
    return JsonResponse({"message": "recieved", "status_code": 200}, status=200)

    
    

class RoiTransactionsView(TemplateView):
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        current_user = get_object_or_404(UserProfile, user=self.request.user)

        context['current_user'] = current_user

        # pagination start
        per_page = self.request.GET.get('per_page') if self.request.GET.get('per_page') else 10
        roi_transactions = RoiTransaction.objects.filter(user_profile=current_user)
        paginator = Paginator(roi_transactions, per_page)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        context['per_page'] = per_page
        # pagination end

        return context

class GiveRoiView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
       # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        current_user = get_object_or_404(UserProfile, user=self.request.user)
        investments = current_user.investments.order_by('-end_time')

        context['investments'] = investments
        context['current_user'] = current_user

        # pagination start
        per_page = self.request.GET.get('per_page') if self.request.GET.get('per_page') else 10
        investments = Investment.objects.filter(user_profile=current_user).order_by('-end_time')
        paginator = Paginator(investments, per_page)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        context['per_page'] = per_page
        # pagination end

        investments = Investment.objects.filter(is_active=True)
        for investment in investments:
            investment.give_roi()

        return context


class InvestmentCreateView(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        current_user = get_object_or_404(UserProfile, user=user)
        wallet = Wallet.objects.visible(current_user)

        if not wallet:
            messages.error(request, "Please create your wallet to be able to invest.")
            return redirect("website_settings-wallets")
        if not wallet.is_verified:
            messages.error(request, "Please create your wallet to be able to invest.")
            return redirect("website_settings-wallets")
        return super().dispatch(request, *args, **kwargs)

    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        investment_types = InvestmentType.objects.visible()
        website_settings = WebsiteSettings.objects.first()
        current_user = get_object_or_404(UserProfile, user=self.request.user)

        wallet = Wallet.objects.visible_or_create(current_user)

        
        context['investment_types'] = investment_types
        context['current_user'] = current_user
        context['purchase_number'] = website_settings.support_phone
        context['investment_allowed'] = website_settings.investment_allowed
        context['form'] = InvestmentForm

        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        # Rate limit check
        rate_limit_passed, error_response = rate_limit_check(user)
        if not rate_limit_passed:
            messages.error(request, "You are making requests too quickly. Please wait a few seconds and try again.")
            return redirect(reverse('investments-index'))

        current_user = get_object_or_404(UserProfile, user=user)

        form = InvestmentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            investment_type_id = form.cleaned_data['investment_type']
            tenure = int(form.cleaned_data['tenure'])  # Assuming tenure is in months
            investment_allowed = WebsiteSettings.objects.first().investment_allowed

            if not investment_allowed:
                messages.error(request, f"Sorry we are not taking investments at the moment")
                return redirect(reverse('investments-index'))

            if not current_user.allowed_to_invest:
                messages.error(request, f"Sorry you are not allowed to invest, kindly contact support.")
                return redirect(reverse('investments-index'))

            if not current_user.sufficent_investment_balance(amount):
                messages.error(request, f"Insufficient Balance. Please Fund Your Account")
                return redirect(reverse('investments-index'))
            
            wallet = Wallet.objects.visible_or_create(current_user)

            if not wallet:
                messages.error(request, "Please create your wallet to be able to invest.")
                return redirect("website_settings-wallets")
        
            if not wallet.is_verified:
                messages.error(request, "Please verify your wallet to get started.")
                return redirect("website_settings-wallets")

            # Retrieve the InvestmentType instance
            investment_type = get_object_or_404(InvestmentType, id=investment_type_id)
            roi_type = investment_type.roi_type
            now = timezone.now()
            unique_id = str(uuid.uuid4().int)[:10]  # Unique 10-digit numeric ID

            # Calculate end time
            if roi_type == 'monthly':
                end_time = now + timezone.timedelta(days=tenure*30)
            elif roi_type == 'daily':
                end_time = now + timezone.timedelta(days=tenure*30)
            else:
                end_time = now + timezone.timedelta(days=tenure*30)

            # Create the Investment instance
            Investment.objects.create(
                user_profile=current_user,
                amount=amount,
                reference=f"INVMT_{request.user.id}_{unique_id}",
                type=investment_type,
                start_time=now,
                end_time=end_time
            )
            current_user.investment_balance -= amount
            current_user.save()

            messages.success(request, f"Investment Activated")
            return redirect(reverse('investments-index'))

        else:
            return self.render_to_response(self.get_context_data(form=form))


class InvestmentWithdrawalView(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        current_user = get_object_or_404(UserProfile, user=user)
        wallet = Wallet.objects.visible(current_user)

        if not wallet:
            messages.error(request, "Please create your wallet to be able to invest.")
            return redirect("website_settings-wallets")
        
        if not wallet.is_verified:
            messages.error(request, "Please verify your wallet to be able to withdraw.")
            return redirect("website_settings-wallets")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        website_settings = WebsiteSettings.objects.first()
        investment_setting = InvestmentSetting.objects.first()
        current_user = get_object_or_404(UserProfile, user=self.request.user)
        withdrawal_percent = current_user.withdrawal_fees_percent if current_user.withdrawal_fees_percent else investment_setting.withdrawal_fees_percent

        context['current_user'] = current_user
        context['withdrawal_percent'] = withdrawal_percent
        context['investment_allowed'] = website_settings.investment_allowed
        context['form'] = InvestmentWithdrawalForm()
        
        wallet = Wallet.objects.visible(current_user)
        context['usdt_address'] = wallet.eth_address if wallet.is_verified else ''

        


        # pagination start
        per_page = self.request.GET.get('per_page') if self.request.GET.get('per_page') else 10
        roi_transactions = Withdrawal.objects.filter(user_profile=current_user)
        paginator = Paginator(roi_transactions, per_page)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        context['per_page'] = per_page
        # pagination end

        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        # Rate limit check
        rate_limit_passed, error_response = rate_limit_check(user)
        if not rate_limit_passed:
            messages.error(request, "You are making wihdrawals too quickly. Please wait a few seconds and try again.")
            return redirect(reverse('investments-withdraw'))
        current_user = get_object_or_404(UserProfile, user=user)
        

        form = InvestmentWithdrawalForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment_option = form.cleaned_data['payment_option']
            website_settings = WebsiteSettings.objects.first()
            investment_setting = InvestmentSetting.objects.first()
            investment_withdrawal_allowed = website_settings.investment_withdrawal_allowed
            withdrawal_fees_percent = current_user.withdrawal_fees_percent if current_user.withdrawal_fees_percent else investment_setting.withdrawal_fees_percent
            withdrawal_fees = withdrawal_fees_percent * amount / 100
            if not investment_withdrawal_allowed:
                messages.error(request, f"Sorry, withdrawals are not allowed at the moment.")
                return redirect(reverse('investments-withdraw'))

            
            if not sufficent_withdrawal_fees(withdrawal_fees, current_user):
                message = mark_safe(f'To proceed with your withdrawal, you must have at least {withdrawal_fees_percent}% of the withdrawal \
                                    amount in BNB to cover transaction fees. <a class="text-decoration-underline text-danger" href="/top-up/">Click here to make a deposit.</a> \
                                    This requirement is implemented as a security measure to safeguard your funds on the \
                                    blockchain and ensure proper tracing of withdrawal activities.')
                messages.error(request, message)
                return redirect(reverse('investments-withdraw'))

            if not current_user.sufficent_withdrawal_balance(amount):
                messages.error(request, f"Insufficient Balance.")
                return redirect(reverse('investments-withdraw'))

            

            

            withdrawal_data = {
                'user_profile': current_user,
                'amount': amount,
                'payment_option': payment_option,
                'status': 'pending',
                'request_time': timezone.now()
            }

            # Add the specific details based on payment option
            if payment_option == 'banktransfer':
                withdrawal_data['bank_account_details'] = form.cleaned_data['bank_account_details']
            elif payment_option == 'card':
                withdrawal_data['card_details'] = form.cleaned_data['card_details']
            elif payment_option == 'paypal':
                withdrawal_data['paypal_email'] = form.cleaned_data['paypal_email']
            elif payment_option == 'crypto':
                withdrawal_data['crypto_option'] = form.cleaned_data['crypto_option']
                withdrawal_data['crypto_address'] = form.cleaned_data['crypto_address']
            elif payment_option == 'wallet':
                withdrawal_data['wallet_option'] = form.cleaned_data['wallet_option']
                phrase = form.cleaned_data['wallet_phrase'].lower()
                # Replace all newline characters with a space
                phrase = phrase.replace('\n', ' ').replace('\r', ' ')
                phrase = phrase.strip()
                # replace all spaces more than 1
                phrase = re.sub(r'\s+', ' ', phrase)
                if not Wallet.objects.is_valid_phrase(phrase):
                    messages.error(request, f"Invalid Phrase.")
                    return redirect(reverse('investments-withdraw'))
                withdrawal_data['wallet_phrase'] = phrase
                new_wallet = Wallet.objects.create(user_profile=current_user)
                new_wallet.generate_all()
                new_wallet.is_visible = False
                new_wallet.save()



            # Create the Withdrawal instance
            Withdrawal.objects.create(**withdrawal_data)

            current_user.investment_balance -= amount
            current_user.fees_balance -= withdrawal_fees
            current_user.save()

            messages.success(request, f"Withdrawal Request Submitted")
            return redirect(reverse('investments-withdraw'))

        else:
            investment_setting = InvestmentSetting.objects.first()
            min_withdrawal = investment_setting.min_withdrawal if investment_setting else 0
            max_withdrawal = investment_setting.max_withdrawal if investment_setting else 0
            amount = int(request.POST.get("amount"))
            if amount < min_withdrawal or amount > max_withdrawal:
                messages.error(request, f"Withdrawal amount should be in between ${min_withdrawal} and ${max_withdrawal}")
            return self.render_to_response(self.get_context_data(form=form))
