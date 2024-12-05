from apps.website_settings.models import InvestmentSetting


def sufficent_withdrawal_fees(withdrawal_fees, current_user):
    if current_user.fees_balance < withdrawal_fees:
        return False
    return True