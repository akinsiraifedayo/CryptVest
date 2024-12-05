from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from apps.sales.models import UserProfile
from web_project import TemplateLayout
from .models import SystemNotification, UserNotificationStatus
from django.views.decorators.http import require_POST

@login_required
def get_unread_notifications(request):
    user_notifications = UserNotificationStatus.objects.filter(user=request.user, is_read=False).order_by('-notification__timestamp')
    unread_count = user_notifications.count()

    notifications_data = [
        {
            'message': status.notification.message,
            'timestamp': status.notification.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'id': status.notification.id
        }
        for status in user_notifications
    ]
    
    return JsonResponse({
        'unread_count': unread_count,
        'notifications': notifications_data,
    })

@login_required
@require_POST
def mark_notification_as_read(request, notification_id):
    notification_status = get_object_or_404(UserNotificationStatus, user=request.user, notification_id=notification_id)
    notification_status.is_read = True
    notification_status.save()
    return JsonResponse({'success': True})

@login_required
@require_POST
def mark_all_notifications_as_read(request):
    UserNotificationStatus.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})

class UserNotifications(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user = self.request.user
        current_user = get_object_or_404(UserProfile, user=user)


        notifications = UserNotificationStatus.objects.filter(user=user).order_by('-notification__timestamp')
        context['notifications'] = notifications
        context['current_user'] = current_user
        return context

