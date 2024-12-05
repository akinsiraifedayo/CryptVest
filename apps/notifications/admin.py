from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SystemNotification, UserNotificationStatus
from .forms import SystemNotificationForm, UserSpecificNotificationForm
from django.contrib.auth.models import User

class NotificationAdmin(admin.ModelAdmin):

    # URL patterns for custom actions
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send-system-notification/', self.admin_site.admin_view(self.send_system_notification), name='send_system_notification'),
            path('send-user-notification/', self.admin_site.admin_view(self.send_user_specific_notification), name='send_user_specific_notification'),
        ]
        return custom_urls + urls

    # View for sending system-wide notifications
    def send_system_notification(self, request):
        if request.method == 'POST':
            form = SystemNotificationForm(request.POST)
            if form.is_valid():
                message = form.cleaned_data['message']
                icon = form.cleaned_data['icon']
                self.create_system_notification(message, icon)
                messages.success(request, "System-wide notification sent successfully!")
                return redirect('admin:index')
        else:
            form = SystemNotificationForm()

        context = {
            'form': form,
            'title': 'Send System Notification',
        }
        return render(request, 'admin/send_notification.html', context)

    # View for sending user-specific notifications
    def send_user_specific_notification(self, request):
        if request.method == 'POST':
            form = UserSpecificNotificationForm(request.POST)
            if form.is_valid():
                users = form.cleaned_data['users']
                message = form.cleaned_data['message']
                icon = form.cleaned_data['icon']
                self.create_user_specific_notification(message, users, icon)
                messages.success(request, "User-specific notification sent successfully!")
                return redirect('admin:index')
        else:
            form = UserSpecificNotificationForm()

        context = {
            'form': form,
            'title': 'Send User-Specific Notification',
        }
        return render(request, 'admin/send_notification.html', context)

    # Create system-wide notification and attach to all users
    def create_system_notification(self, message, icon=None):
        notification = SystemNotification.objects.create(message=message, icon=icon)
        users = User.objects.filter(is_active=True)
        notifications_status = [
            UserNotificationStatus(user=user, notification=notification)
            for user in users
        ]
        UserNotificationStatus.objects.bulk_create(notifications_status)

    # Create user-specific notification
    def create_user_specific_notification(self, message, users, icon=None):
        notification = SystemNotification.objects.create(message=message, icon=icon)
        notifications_status = [
            UserNotificationStatus(user=user, notification=notification)
            for user in users
        ]
        UserNotificationStatus.objects.bulk_create(notifications_status)

    # Add links to the Django admin menu
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_buttons'] = [
            {
                'title': 'Send System Notification',
                'url': 'send-system-notification/'
            },
            {
                'title': 'Send User-Specific Notification',
                'url': 'send-user-notification/'
            }
        ]
        return super().changelist_view(request, extra_context=extra_context)

# Register the admin class
admin.site.register(SystemNotification, NotificationAdmin)
