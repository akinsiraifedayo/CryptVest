import os
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.conf import settings

from apps.sales.models import UserProfile
from apps.sales.utils import rate_limit_check
from apps.referrals.models import ReferralWithdrawal

from apps.website_settings.models import WebsiteSettings
from .forms import ReferralWithdrawalForm

from django.core.paginator import Paginator

# Create your views here.

class ReferralsView(TemplateView):

    # Predefined function
    def get_context_data(self, **kwargs):
        SUBDOMAIN_NAME = os.getenv('SUBDOMAIN_NAME', '')
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        current_user = get_object_or_404(UserProfile, user=self.request.user)
        website_settings = WebsiteSettings.objects.first()
        if website_settings:
            if current_user.account_type == "merchant":
                context['referral_percentage'] = website_settings.merchant_referral_percentage
                context['referral_allowed'] = website_settings.merchant_referral_allowed
            else:
                context['referral_percentage'] = website_settings.referral_percentage
                context['referral_allowed'] = website_settings.referral_allowed
            context['referral_code'] = current_user.referral_code




        context['current_user'] = current_user
        context['website_url'] =  f'https://{SUBDOMAIN_NAME}/register'

        # pagination start
        per_page = self.request.GET.get('per_page') if self.request.GET.get('per_page') else 10
        referred_users_list = UserProfile.objects.filter(referred_by=current_user).order_by('-id')
        paginator = Paginator(referred_users_list, per_page)  # Show 10 users per page.
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        context['per_page'] = per_page
        # pagiunation end
        return context

class ReferralWithdrawalView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        current_user = get_object_or_404(UserProfile, user=self.request.user)

        context['current_user'] = current_user
        context['form'] = ReferralWithdrawalForm()




        # pagination start
        per_page = self.request.GET.get('per_page') if self.request.GET.get('per_page') else 10
        roi_transactions = ReferralWithdrawal.objects.filter(user_profile=current_user)
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
            messages.error(request, "You are making requests too quickly. Please wait a few seconds and try again.")
            return redirect(reverse('referral-withdrawal'))
        current_user = get_object_or_404(UserProfile, user=user)


        form = ReferralWithdrawalForm(request.POST)
        if form.is_valid():
            minimum_withdrawal = 5000
            amount = form.cleaned_data['amount']
            payment_option = form.cleaned_data['payment_option']
            referral_withdrawal_allowed = WebsiteSettings.objects.first().referral_withdrawal_allowed

            if not referral_withdrawal_allowed:
                messages.error(request, f"Sorry, withdrawals are not allowed at the moment")
                return redirect(reverse('referral-withdrawal'))

            if not current_user.sufficent_referral_withdrawal_balance(amount):
                messages.error(request, f"Insufficient Balance. Please check your referral balance.")
                return redirect(reverse('referral-withdrawal'))

            if payment_option != 'databalance' and amount < minimum_withdrawal:
                messages.error(request, f"Minumum withdrawal is {minimum_withdrawal} for the selected payment option. You can withdraw by 'Adding To Balance' instead.")
                return redirect(reverse('referral-withdrawal'))

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
            elif payment_option == 'databalance':
                withdrawal_data['status'] = 'completed'
                withdrawal_data['processed_time'] = timezone.now()
            # Create the Withdrawal instance
            ReferralWithdrawal.objects.create(**withdrawal_data)

            current_user.referral_balance -= amount
            if payment_option == 'databalance':
                current_user.investment_balance += amount
            current_user.save()


            messages.success(request, f"Withdrawal Request Submitted")
            return redirect(reverse('referral-withdrawal'))

        else:
            return self.render_to_response(self.get_context_data(form=form))
