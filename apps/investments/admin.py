from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from apps.investments.models import Withdrawal, Investment, InvestmentType, RoiTransaction, Wallet
from django.utils import timezone

# Register your models here.

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'amount', 'status', 'processed_time')
    list_filter = ('status',)
    search_fields = ('status', 'amount')

    def save_model(self, request, obj, form, change):
        if change:  # Only update processed_time if this is an edit
            if obj.status in ['completed', 'failed'] and 'status' in form.changed_data:
                obj.processed_time = timezone.now()
        super().save_model(request, obj, form, change)

admin.site.register(Investment)
admin.site.register(InvestmentType)
admin.site.register(Wallet)
admin.site.register(RoiTransaction)
