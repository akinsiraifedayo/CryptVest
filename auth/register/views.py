from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.conf import settings
from apps.investments.models import Wallet
from auth.views import AuthView
# from auth.helpers import send_verification_email
from apps.mail.utils import send_verification_email
from auth.models import Profile
from apps.sales.models import UserProfile
import uuid
from django.utils import timezone
from datetime import timedelta


class RegisterView(AuthView):
    def get(self, request):
        if request.user.is_authenticated:
            # If the user is already logged in, redirect them to the home page or another appropriate page.
            return redirect("/")  # Replace 'index' with the actual URL name for the home page

        # Render the login page for users who are not logged in.
        return super().get(request)

    def post(self, request):
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone_number = request.POST.get("phone_number")
        referral_code = request.POST.get("referral_code")



        # Check if a user with the same username or email already exists
        if User.objects.filter(username=username, email=email).exists():
            messages.error(request, "User already exists, Try logging in.")
            return redirect("register")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")
        if referral_code:
            referral_code = referral_code.lower()
            referred_by_profile = UserProfile.objects.filter(referral_code=referral_code).first()
            if not referred_by_profile:
                messages.error(request, "Invalid Referral Code")
                return redirect("register")

        # Create the user and set their password
        created_user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        created_user.set_password(password)
        created_user.save()

        # Add the user to the 'client' group (or any other group you want to use as default for new users)
        user_group, created = Group.objects.get_or_create(name="client")
        created_user.groups.add(user_group)

        # Generate a token and send a verification email here
        token = str(uuid.uuid4())

        # Set the token in the user's profile
        user_profile, created = Profile.objects.get_or_create(user=created_user)
        user_profile.email_token = token
        user_profile.email = email
        user_profile.save()

        current_user_profile = get_object_or_404(UserProfile, user=created_user)
        if current_user_profile:
            new_wallet = Wallet.objects.create(user_profile=current_user_profile)
            new_wallet.generate_all()
            current_user_profile.phone_number = phone_number

            if referral_code:
                if referred_by_profile:
                    current_user_profile.referred_by = referred_by_profile

            if settings.DEFAULT_MEMBERSHIP == 'vendor':
                now = timezone.now()
                one_year_from_now = now + timedelta(days=365)  # 1 year from now
                current_user_profile.account_type = 'vendor'
                current_user_profile.expiry_date = one_year_from_now


            current_user_profile.save()



        # send_verification_email(email, token)
        send_verification_email(created_user, token)

        if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
            messages.success(request, "Verification email sent successfully")
        else:
            messages.error(request, "We are currently experiencing a high volume of activity on our servers, which is causing a temporary delay in sending out verification emails. \
                \nPlease rest assured that we are actively working to reduce the load, and you will receive your verification email as soon as normal operations are restored. \
                \nIn the meantime, you can skip the verification process for now and continue to log in and use your account without interruption.")

        request.session['email'] = email ## Save email in session
        # Redirect to the verification page after successful registration
        return redirect("verify-email-page")
