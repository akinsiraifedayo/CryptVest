from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from apps.sales.models import UserProfile



@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def change_referral_code(request):
    current_user = get_object_or_404(UserProfile, user=request.user)

    new_referral_code = request.data.get('referral_code').lower()
    if new_referral_code == current_user.referral_code:
        return Response({"message": "Referral code updated successfully"})

    if not new_referral_code:
        return Response({"error": "Referral code is required"})

    if len(new_referral_code) > 15:
        return Response({"error": "Referral code must be 15 characters or less"})

    # Check if the new referral code already exists
    if UserProfile.objects.filter(referral_code=new_referral_code).exists():
        return Response({"error": "Referral code already in use by someone else"})

    current_user.referral_code = new_referral_code
    current_user.save()

    return Response({"message": "Referral code updated successfully"})
