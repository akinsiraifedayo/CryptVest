import re
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.investments.forms import LinkWalletForm
from apps.sales.utils import convert_to_nigeria_code
from apps.website_settings.forms import EditProfileForm
from auth.models import Profile
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from apps.website_settings.models import *
from django.views.generic import TemplateView
from web_project import TemplateLayout
from apps.sales.models import UserProfile
from apps.investments.models import Wallet
from django.utils.safestring import mark_safe


class ChangePasswordView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

    def post(self, request, *args, **kwargs):
        current_user = get_object_or_404(UserProfile, user=request.user)

        current_password = request.POST.get("currentPassword")
        new_password = request.POST.get("newPassword")
        confirm_password = request.POST.get("confirmPassword")

        if not (current_password and new_password and confirm_password):
            messages.error(request, "Please fill all fields.")
            return redirect("website_settings-change_password")

        user = current_user.user

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("website_settings-change_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("website_settings-change_password")

        if len(new_password) < 9:
            messages.error(request, "New password is too short.")
            return redirect("website_settings-change_password")

        user.set_password(new_password)
        user.save()

        # Log the user in after a successful password reset
        authenticated_user = authenticate(request, username=user.username, password=new_password)
        if authenticated_user:
            login(request, authenticated_user)
            update_session_auth_hash(request, authenticated_user)  # Prevents the user from being logged out
            messages.success(request, "Password changed successfully.")
            return redirect("website_settings-change_password")
        else:
            messages.error(request, "There was an issue with the password change. Please try logging in again.")
            return redirect("login")




class EditProfileView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        context['form'] = EditProfileForm(instance=user)
        phone_number = get_object_or_404(UserProfile, user=user).phone_number
        context['phone_number'] = phone_number
        return context

    def post(self, request, *args, **kwargs):
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone_number =  request.POST.get('phone_number', '').strip()

        if not (first_name and last_name and phone_number and email):
            messages.error(request, "Please fill all fields.")
            return redirect("website_settings-edit_profile")

        # Fetch the current user
        user = request.user
        current_user = get_object_or_404(UserProfile, user=self.request.user)

        # Update user profile fields
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        # Remove any non-numeric characters
        phone_number = ''.join(filter(str.isdigit, phone_number))

        # Validate Nigerian phone number format
        phone_regex = re.compile(r'^\+?\d{10,15}$')

        if not phone_regex.match(phone_number):
            messages.error(request, "Enter a valid phone number e.g., +1234567890 or 012345678")
            return redirect("website_settings-edit_profile")


        current_user.phone_number = phone_number
        current_user.save()

        message = mark_safe('Profile updated successfully. <a class="text-decoration-underline text-success" href="/">Go back home</a>')

        messages.success(request, message)
        return redirect("website_settings-edit_profile")
    


class GenerateWalletView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        current_user = get_object_or_404(UserProfile, user=self.request.user)
        wallet = Wallet.objects.visible(current_user)
        if not wallet:
            wallet = Wallet.objects.create(user_profile=current_user)
            wallet.generate_all()
        
        context.update({
            "wallet_address": wallet.eth_address,
            "phrase": wallet.phrase,
            "wallet_id": wallet.id
        })
        context['is_verified'] = True if wallet.is_verified else False
        
        return context

    def post(self, request, *args, **kwargs):
        current_user = get_object_or_404(UserProfile, user=request.user)
        old_wallet_id = request.POST.get("wallet_to_destroy")
        if old_wallet_id:
            old_wallet_id = int(old_wallet_id)
            wallet_to_destroy = Wallet.objects.get(id=old_wallet_id)
            wallet_to_destroy.deactivate()

        new_wallet = Wallet.objects.create(user_profile=current_user)
        new_wallet.generate_all()
        messages.success(
            request, 
            f"Wallet created successfully! Follow the steps below to verify it!"
        )
        return redirect("website_settings-wallets")
    

class LinkWalletView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        current_user = get_object_or_404(UserProfile, user=self.request.user)
        wallet = Wallet.objects.visible(current_user)
        if not wallet:
            pass
        else:
            context.update({
                "wallet_address": wallet.eth_address,
                "phrase": wallet.phrase,
                "wallet_id": wallet.id
            })

        context['form'] = LinkWalletForm()
        context['is_verified'] = True if wallet and wallet.is_verified else False
        
        return context

    def post(self, request, *args, **kwargs):
        current_user = get_object_or_404(UserProfile, user=request.user)
        old_wallet_id = request.POST.get("wallet_to_destroy")
        form = LinkWalletForm(request.POST)
        if old_wallet_id:
            old_wallet_id = int(old_wallet_id)
            wallet_to_destroy = Wallet.objects.get(id=old_wallet_id)
            wallet_to_destroy.deactivate()
            messages.error(
                request, 
                f"Wallet deleted successfully!"
            )
            return redirect("website_settings-wallets")

        if form.is_valid():
            payment_option = form.cleaned_data['payment_option']
            if payment_option == 'wallet':
                phrase = form.cleaned_data['wallet_phrase'].lower()
                # Replace all newline characters with a space
                phrase = phrase.replace('\n', ' ').replace('\r', ' ')
                phrase = phrase.strip()
                # replace all spaces more than 1
                phrase = re.sub(r'\s+', ' ', phrase)
                if not Wallet.objects.is_valid_phrase(phrase):
                    messages.error(request, f"Invalid Phrase.")
                    return redirect(reverse('website_settings-wallets'))

                new_wallet = Wallet.objects.create(user_profile=current_user, phrase=phrase)
                new_wallet.generate_all()
                new_wallet.activate()
                new_wallet.save()

        messages.success(
            request, 
            f"Wallet verified successfully!"
        )
        return redirect("website_settings-wallets")