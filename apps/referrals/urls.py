from django.urls import path

from apps.referrals.utils import change_referral_code
from apps.referrals.views import ReferralsView, ReferralWithdrawalView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path(
        "app/referrals/",
        login_required(ReferralsView.as_view(template_name="referrals.html")),
        name="all-referrals",
    ),
    path(
        "app/change-referral-code/",
        login_required(change_referral_code),
        name="change-referral-code",
    ),
    # path(
    #     "app/investments/create/",
    #     login_required(InvestmentCreateView.as_view(template_name="investment_create.html")),
    #     name="create",
    # ),
    # path(
    #     "app/investments/roi_transactions/",
    #     login_required(RoiTransactionsView.as_view(template_name="roi_transactions.html")),
    #     name="roi_transactions",
    # ),
    # path(
    #     "app/investments/give_roi/",
    #     login_required(GiveRoiView.as_view(template_name="investments.html")),
    #     name="give_roi",
    # ),
    path(
        "app/referrals/withdraw/",
        login_required(ReferralWithdrawalView.as_view(template_name='referral_withdrawal.html')),
        name="referral-withdrawal",
    )

]
