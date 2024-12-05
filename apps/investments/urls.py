from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

# app_name = 'investments'

urlpatterns = [
    path(
        "app/investments/",
        login_required(IndexView.as_view(template_name="investments.html")),
        name="investments-index",
    ),
    path(
        "app/investments/create/",
        login_required(InvestmentCreateView.as_view(template_name="investment_create.html")),
        name="investments-create",
    ),
    path(
        "app/investments/roi_transactions/",
        login_required(RoiTransactionsView.as_view(template_name="roi_transactions.html")),
        name="investments-roi_transactions",
    ),
    # path(
    #     "app/investments/give_roi/",
    #     login_required(GiveRoiView.as_view(template_name="investments.html")),
    #     name="investments-give_roi",
    # ),
    path(
        "app/investments/withdraw/",
        login_required(InvestmentWithdrawalView.as_view(template_name='investment_withdrawal.html')),
        name="investments-withdraw",
    ),
    path(
        "app/get_wallets_to_refresh/<str:signature>/",
        get_wallets_to_refresh,
        name="get_sim",
    ),

]
