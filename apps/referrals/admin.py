from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from apps.referrals.models import ReferralWithdrawal
from django.utils import timezone

# Register your models here.

@admin.register(ReferralWithdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'amount', 'status', 'payment_option', 'processed_time')
    list_filter = ('status',)
    search_fields = ('status', 'amount')

    def save_model(self, request, obj, form, change):
        if change:  # Only update processed_time if this is an edit
            if obj.status in ['completed', 'failed'] and 'status' in form.changed_data:
                obj.processed_time = timezone.now()
        super().save_model(request, obj, form, change)
