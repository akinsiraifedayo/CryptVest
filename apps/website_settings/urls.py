from django.urls import path
from apps.website_settings.views import EditProfileView, ChangePasswordView, GenerateWalletView, LinkWalletView
from django.contrib.auth.decorators import login_required
from apps.website_settings.utils import verify_usdt_bep20, move_wallet_to_investment, move_wallet_to_fees

urlpatterns = [
    path(
        "app/change_password/",
        login_required(ChangePasswordView.as_view(template_name="change_password.html")),
        name="website_settings-change_password",
    ),
    path(
        "app/edit_profile/",
        login_required(EditProfileView.as_view(template_name="edit_profile.html")),
        name="website_settings-edit_profile",
    ),


    path(
        "app/wallet/",
        login_required(GenerateWalletView.as_view(template_name="change_phrase.html")),
        name="website_settings-wallets",
    ),
    # path(
    #     "app/wallet/",
    #     login_required(LinkWalletView.as_view(template_name="link_phrase.html")),
    #     name="website_settings-wallets",
    # ),


    path(
        "app/wallet/verify/",
        login_required(verify_usdt_bep20),
        name="website_settings-verify",
    ),
    path(
        "app/wallet/move-to-investment/",
        login_required(move_wallet_to_investment),
        name="website_settings-move_wallet_to_investment",
    ),
    path(
        "app/wallet/move-to-fees/",
        login_required(move_wallet_to_fees),
        name="website_settings-move_wallet_to_fees",
    )

]
