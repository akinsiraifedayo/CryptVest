from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
import os
from apps.website_settings.models import WebsiteSettings
from django.templatetags.static import static


SUBDOMAIN_NAME = os.getenv('SUBDOMAIN_NAME', '')

def get_static_url(file_path):
    return static(file_path)

def send_email(subject, email, message_html, message_plain):
    try:
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        email_message = EmailMultiAlternatives(subject, message_plain, email_from, recipient_list)
        email_message.attach_alternative(message_html, "text/html")
        email_message.send()
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_verification_email(user, token):
    subject = "Verify your email"
    verification_url = f"https://{SUBDOMAIN_NAME}/verify/email/{token}/"

    # Context for the email template
    support_email = WebsiteSettings.objects.first().support_email
    logo_static_path = get_static_url('img/mail/logo.png')
    logo_url = f'https://{SUBDOMAIN_NAME}{logo_static_path}'

    context = {
        'APP_NAME': settings.THEME_VARIABLES.get("template_name"),
        'APP_SITE': f'https://{SUBDOMAIN_NAME}',
        'VERIFICATION_URL': verification_url,
        'SUPPORT_EMAIL': support_email,
        'LOGO_URL': logo_url,
        'USER': user
    }

    # Render the HTML template
    message_html = render_to_string('mail-verify-email.html', context)
    # Fallback plain-text message
    message_plain = f"Hi,\n\nPlease verify your email using this link: {verification_url}"

    send_email(subject, user.email, message_html, message_plain)
