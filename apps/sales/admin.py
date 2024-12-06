from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from .models import *
from apps.sales.forms import *
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.db.models import Sum
# Register your models here.


def add_balance(modeladmin, request, queryset):
    amount = 100  # Specify the amount to add or prompt the admin for this value
    for profile in queryset:
        profile.add_balance_from_admin(amount, request.user)

add_balance.short_description = 'Add balance to selected users'


class DataPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'retailer_price', 'vendor_price', 'data_qty')
    search_fields = ('name',)
    list_filter = ('retailer_price',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')
    search_fields = ('user__username','user__email')
    change_form_template = 'admin/userprofile_change_form.html'
    list_filter = ('account_type',)

    # change_form_template = 'admin/add_balance_form.html'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:user_id>/add_balance/', self.admin_site.admin_view(self.add_balance)),
        ]
        return custom_urls + urls

    def add_balance(self, request, user_id):
        user_profile = self.get_object(request, user_id)
        if request.method == 'POST':
            form = AddBalanceForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']
                user_profile.add_balance_from_admin(amount, request.user)
                self.message_user(request, f"Added {amount} to {user_profile.user.username}'s balance.")
                return HttpResponseRedirect("..")
        else:
            form = AddBalanceForm()

        context = dict(
            self.admin_site.each_context(request),
            form=form,
            user_profile=user_profile,
        )
        return TemplateResponse(request, 'admin/add_balance_form.html', context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['add_balance_url'] = f'../../{object_id}/add_balance/'
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profiles'

class UserAdmin(DefaultUserAdmin):
    inlines = (UserProfileInline,)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        UserProfile.objects.get_or_create(user=obj)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_filter = ('user_profile__account_type', 'timestamp',)
    list_display = ('user_profile', 'package', 'phone_number', 'timestamp', 'id', 'sim_number')
    search_fields = ('user_profile__user__username','id', 'phone_number','sim__phone_number')

    # readonly_fields = ('total_amount_today',)

    def total_amount_today(self, obj):
        # Calculate the total amount for today's transactions
        total = self.get_queryset(self).aggregate(Sum('amount'))['amount__sum']
        return total or 0

    total_amount_today.short_description = 'Total Amount Today'

class AccountFunctionInline(admin.TabularInline):
    model = AccountFunction
    extra = 1

class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'exact_name', 'monthly_price', 'yearly_price')
    inlines = [AccountFunctionInline]

@admin.register(OnlineTransaction)
class OnlineTransactionAdmin(admin.ModelAdmin):
    list_filter = ('status', 'created_at')
    list_display = ('amount', 'reference', 'status', 'created_at', 'user_profile')
    search_fields = ('reference','user_profile__user__username')

@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'event_type', 'transaction_reference', 'status')
    list_filter = ('event_type', 'status', 'timestamp')
    search_fields = ('transaction_reference', 'event_type', 'payload')
    readonly_fields = ('timestamp', 'event_type', 'transaction_reference', 'payload', 'status')

    def has_add_permission(self, request):
        return False  # Disable adding new records via the admin interface

    def has_delete_permission(self, request, obj=None):
        return False  # Disable deleting records via the admin interface

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(AdminTransaction)
admin.site.register(AccountType, AccountTypeAdmin)

admin.site.register(AccountFunction)
# admin.site.register(UserRequest)
