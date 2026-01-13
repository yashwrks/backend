from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.utils.timezone import localtime
from home.models import PhoneOTP


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # ---------------- USER INFO ----------------
        user_data = {
            "id": user.id,
            "name": user.first_name,
            "phone": user.username,   # phone stored as username
            "email": user.email,
            "joined_at": user.date_joined.date()
        }

        # ---------------- PHONE OTP INFO ----------------
        otp_obj = PhoneOTP.objects.filter(
            phone=user.username
        ).order_by("-created_at").first()

        phone_verified = False
        otp_attempts_used = 0

        if otp_obj:
            phone_verified = not otp_obj.is_expired()
            otp_attempts_used = otp_obj.attempts

        auth_data = {
            "phone_verified": phone_verified,
            "login_method": "OTP",
            "last_login": localtime(user.last_login) if user.last_login else None
        }

        # ---------------- STATS ----------------
        stats_data = {
            "total_logins": 1 if user.last_login else 0,
            "last_active": localtime(user.last_login) if user.last_login else None,
            "otp_attempts_used": otp_attempts_used,
            "otp_attempts_limit": 5
        }

        # ---------------- ACTIVE PLAN ----------------
        plan_data = {
            "name": "Free",
            "status": "Active",
            "valid_till": None,
            "can_upgrade": True
        }

        return Response({
            "user": user_data,
            "auth": auth_data,
            "stats": stats_data,
            "plan": plan_data
        })
