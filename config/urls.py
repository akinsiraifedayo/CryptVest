"""
URL configuration for web_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from web_project.views import SystemView

urlpatterns = [
    path("admin/", admin.site.urls),

    # FrontPages urls
    path("", include("apps.mail.urls")),

    # User urls
    path("", include("apps.users.urls")),

    # auth urls
    path("", include("auth.urls")),

    # transaction urls
    path("", include("apps.transactions.urls")),




    # sales urls
    path("", include("apps.sales.urls")),

    #investments urls
    path("", include("apps.investments.urls")),

    # website settings urls
    path("", include("apps.website_settings.urls")),

     # referrals urls
    path("", include("apps.referrals.urls")),
    path("", include("apps.notifications.urls")),

]

handler404 = SystemView.as_view(template_name="pages_misc_error.html", status=404)
handler403 = SystemView.as_view(template_name="pages_misc_not_authorized.html", status=403)
handler400 = SystemView.as_view(template_name="pages_misc_error.html", status=400)
handler500 = SystemView.as_view(template_name="pages_misc_error.html", status=500)
