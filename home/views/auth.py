from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken

from home.models import PhoneOTP
from home.serializers import VerifyOTPSerializer, SignupSerializer
from home.utils.otp import verify_otp

MAX_ATTEMPTS = 5


class SignupView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if User.objects.filter(username=data["phone"]).exists():
            return Response({"error": "User exists"}, status=400)

        User.objects.create(
            username=data["phone"],   # phone = username
            email=data["email"],
            first_name=data["name"],
            password=make_password(data["password"])
        )

        return Response(
            {"message": "Signup successful. Verify phone via OTP"},
            status=status.HTTP_201_CREATED
        )


class VerifyPhoneOTP(APIView):
    permission_classes = []

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

        user = User.objects.get(username=phone)
        refresh = RefreshToken.for_user(user)

        record.delete()

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })
