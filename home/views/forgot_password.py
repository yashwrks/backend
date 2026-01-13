from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny   # ✅ IMPORTANT

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from home.models import PhoneOTP
from home.serializers import SendOTPSerializer, VerifyOTPSerializer
from home.utils.otp import generate_otp, hash_otp, verify_otp
from home.utils.otp_sender import send_otp

MAX_ATTEMPTS = 5


# 🔹 STEP 1: SEND OTP
class ForgotPasswordSendOTP(APIView):
    permission_classes = [AllowAny]   # ✅ FIX

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        if not User.objects.filter(username=phone).exists():
            return Response({"error": "User not found"}, status=404)

        otp = generate_otp()

        # delete old OTP
        PhoneOTP.objects.filter(phone=phone).delete()

        PhoneOTP.objects.create(
            phone=phone,
            otp_hash=hash_otp(otp)
        )

        send_otp(phone, otp)

        return Response(
            {"message": "OTP sent for password reset"},
            status=status.HTTP_200_OK
        )


# 🔹 STEP 2: VERIFY OTP
class VerifyForgotPasswordOTP(APIView):
    permission_classes = [AllowAny]   # ✅ FIX

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        otp = serializer.validated_data["otp"]

        try:
            record = PhoneOTP.objects.get(phone=phone)
        except PhoneOTP.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=400)

        if record.is_expired():
            record.delete()
            return Response({"error": "OTP expired"}, status=400)

        if not verify_otp(otp, record.otp_hash):
            record.attempts += 1
            record.save()

            if record.attempts >= MAX_ATTEMPTS:
                record.delete()
                return Response({"error": "Too many attempts"}, status=400)

            return Response({"error": "Invalid OTP"}, status=400)

        # ✅ OTP verified (do NOT delete yet)
        return Response({"message": "OTP verified"}, status=200)


# 🔹 STEP 3: RESET PASSWORD
class ResetPassword(APIView):
    permission_classes = [AllowAny]   # ✅ FIX

    def post(self, request):
        phone = request.data.get("phone")
        new_password = request.data.get("new_password")

        if not phone or not new_password:
            return Response(
                {"error": "phone and new_password required"},
                status=400
            )

        try:
            record = PhoneOTP.objects.get(phone=phone)
        except PhoneOTP.DoesNotExist:
            return Response(
                {"error": "OTP verification required"},
                status=403
            )

        if record.is_expired():
            record.delete()
            return Response(
                {"error": "OTP expired"},
                status=400
            )

        user = User.objects.get(username=phone)
        user.password = make_password(new_password)
        user.save()

        # 🔥 OTP consumed
        record.delete()

        return Response(
            {"message": "Password reset successful"},
            status=200
        )
