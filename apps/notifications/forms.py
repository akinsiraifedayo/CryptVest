from django import forms
from django.contrib.auth.models import User

class SystemNotificationForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label="Notification Message")
    icon = forms.CharField(max_length=255, required=False, label="Icon (optional)")

class UserSpecificNotificationForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'data-live-search': 'true'}),
        label='Select Users'
    )
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='Notification Message')
    icon = forms.CharField(max_length=255, required=False, label='Icon')
