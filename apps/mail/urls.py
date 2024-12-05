from django.urls import path
from .views import EmailView, VerifyEmailView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path(
        "app/email/",
        login_required(EmailView.as_view(template_name="app_email.html")),
        name="app-email",
    ),
    path(
        "app/email/verify/",
        login_required(VerifyEmailView.as_view(template_name="mail-verify-email.html")),
        name="email-verify",
    ),
]
