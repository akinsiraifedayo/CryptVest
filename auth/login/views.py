from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from auth.views import AuthView
from django.utils.safestring import mark_safe
from django.utils.http import url_has_allowed_host_and_scheme
from apps.sales.models import UserProfile

class LoginView(AuthView):
    def get(self, request):
        if request.user.is_authenticated:
            # If the user is already logged in, redirect them to the home page or another appropriate page.
            return redirect("investments-index")  # Replace 'index' with the actual URL name for the home page

        # Render the login page for users who are not logged in.
        return super().get(request)

    def post(self, request):
        if request.method == "POST":
            username = request.POST.get("email-username")
            password = request.POST.get("password")

            if not (username and password):
                messages.error(request, "Please enter your username and password.")
                return redirect("login")

            create_account_message = mark_safe(
                    "The account you entered does not exist. <a class='text-decoration-underline' href='/register/'>Click here to create a new account.</a>"
                )
            if "@" in username:
                user = User.objects.filter(email=username).first()
                if user is None:
                    messages.error(request, create_account_message)
                    return redirect("login")
                username = user.username

            user = User.objects.filter(username=username).first()
            if user is None:
                messages.error(request, create_account_message)
                return redirect("login")

            authenticated_user = authenticate(request, username=username, password=password)
            if authenticated_user is not None:
                # Login the user if authentication is successful
                login(request, authenticated_user)
                

                # Redirect to the page the user was trying to access before logging in
                next_url = request.GET.get("next")
                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                else:
                    return redirect("investments-index")
            else:
                messages.error(request, "Please enter a valid email and password.")
                return redirect("login")
