from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('notifications/unread/', views.get_unread_notifications, name='get_unread_notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications/read-all/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    # path('notifications/', views.user_notifications, name='user_notifications'),
    path(
        "notifications",
        login_required(views.UserNotifications.as_view(template_name="user_notifications.html")),
        name="user_notifications",
    ),
]
