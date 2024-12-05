from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
import json

from apps.investments.models import Wallet
from apps.sales.models import UserProfile

@csrf_exempt
def verify_usdt_bep20(request):
    if request.method == 'POST':
        current_user = get_object_or_404(UserProfile, user=request.user)
        correct_wallet = Wallet.objects.visible(current_user)
        correct_address = correct_wallet.eth_address

        data = json.loads(request.body)
        wallet_address = data.get('walletAddress')
        wallet_decimal = data.get('walletDecimal')
        
        if wallet_decimal:
            if int(wallet_decimal) != 18:
                return JsonResponse({'error': 'Please ensure you carefully follow the steps outlined above, using the right decimal, and try again.'})
        

        # Example verification logic, replace with actual validation
        if len(wallet_address) == 42 and wallet_address.startswith('0x') and wallet_address == correct_address:
            correct_wallet.activate()
            return JsonResponse({'verified': True})
        else:
            return JsonResponse({'error': 'Invalid wallet address. Please enter a valid BEP-20 address.'})
    else:
        return JsonResponse({'error': 'Invalid Method'})


@csrf_exempt
def move_wallet_to_investment(request):
    current_user = get_object_or_404(UserProfile, user=request.user)
    current_user.transfer_wallet_to_investment()
    return redirect('investments-create')

@csrf_exempt
def move_wallet_to_fees(request):
    current_user = get_object_or_404(UserProfile, user=request.user)
    current_user.transfer_wallet_to_fees()
    return redirect('investments-withdraw')