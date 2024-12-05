from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static

urlpatterns = [
    path(
        "",
        login_required(IndexView.as_view(template_name="index.html")),
        name="index",
    ),
    path(
        "app/faq/",
        login_required(FaqView.as_view(template_name="faq.html")),
        name="sales-faq",
    ),
    path(
        "terms-and-conditions/",
        TermsAndConditionsView.as_view(template_name="tc.html"),
        name="terms-and-conditions",
    ),
    
    # flutterwave

    path(
        "top-up/",
        login_required(TopUpBalanceView.as_view(template_name="top_up_balance.html")),
        name="top_up_balance",
    ),
]


import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development')

if ENVIRONMENT != 'production':
# Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)