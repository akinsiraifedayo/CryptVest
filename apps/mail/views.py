import os
from django.views.generic import TemplateView
from apps.mail.utils import get_static_url
from auth.models import Profile
from web_project import TemplateLayout
from apps.website_settings.models import WebsiteSettings

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to mail/urls.py file for more pages.
"""


class EmailView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

class VerifyEmailView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        SUBDOMAIN_NAME = os.getenv('SUBDOMAIN_NAME', '')

        subject = "Verify your email"
        user=self.request.user
        token = Profile.objects.get(user=self.request.user).email_token
        subject = "Verify your email"
        verification_url = f"https://{SUBDOMAIN_NAME}/verify/email/{token}/"

        # Context for the email template
        support_email = WebsiteSettings.objects.first().support_email
        logo_static_path = get_static_url('img/mail/logo.png')
        logo_url = f'https://{SUBDOMAIN_NAME}{logo_static_path}'

        context.append({
            'APP_NAME': settings.THEME_VARIABLES.get("template_name"),
            'APP_SITE': f'https://{SUBDOMAIN_NAME}',
            'VERIFICATION_URL': verification_url,
            'SUPPORT_EMAIL': support_email,
            'LOGO_URL': logo_url,
            'USER': user
        })
        return context

def send_verification_email(user, verification_url):
    subject = 'Verify Your Email Address'
    from_email = 'your-email@example.com'
    to_email = user.email
    support_email = WebsiteSettings.objects.first().support_email
    context = {
        'APP_NAME': settings.THEME_VARIABLES.get("template_name"),
        'APP_SITE': f'https://{settings.SUBDOMAIN_NAME}',
        'VERIFICATION_URL': verification_url,
        'SUPPORT_EMAIL': support_email,
    }
    html_content = render_to_string('./templates/mail-reset-password.html', context)
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
