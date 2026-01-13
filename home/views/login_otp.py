from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from home.utils.twilio_otp import send_sms_otp
from home.utils.otp import generate_otp, hash_otp
from home.models import PhoneOTP

User = get_user_model()


class LoginSendOTP(APIView):
    permission_classes = []

    def post(self, request):
        phone = request.data.get("phone")
        password = request.data.get("password")

        if not phone or not password:
            return Response(
                {"message": "Phone and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=phone)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=404)

        if not user.check_password(password):
            return Response({"message": "Invalid password"}, status=401)

        otp = generate_otp()

        PhoneOTP.objects.filter(phone=phone).delete()
        PhoneOTP.objects.create(
            phone=phone,
            otp_hash=hash_otp(otp)
        )

        send_sms_otp(phone, otp)

        return Response(
            {"message": "OTP sent to phone"},
            status=status.HTTP_200_OK
        )
