from django.contrib import admin
from .models import WebsiteSettings, InvestmentSetting

@admin.register(WebsiteSettings)
class WebsiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Prevent adding new settings if one already exists
        return not WebsiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of settings
        return False

    def has_change_permission(self, request, obj=None):
        # Allow changing the settings
        return True

@admin.register(InvestmentSetting)
class InvestmentSettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Prevent adding new settings if one already exists
        return not InvestmentSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of settings
        return False

    def has_change_permission(self, request, obj=None):
        # Allow changing the settings
        return True