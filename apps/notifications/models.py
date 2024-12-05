from django.db import models
from django.contrib.auth.models import User

# Model for shared system-wide notifications
class SystemNotification(models.Model):
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    icon = models.CharField(max_length=255, null=True, blank=True)  # Optional icon field

    def __str__(self):
        return f'SystemNotification: {self.message}'

# Model to track whether a user has read a specific notification
class UserNotificationStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification = models.ForeignKey(SystemNotification, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.notification.message} - {"Read" if self.is_read else "Unread"}'
