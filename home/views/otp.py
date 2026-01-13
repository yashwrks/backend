from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from home.models import PhoneOTP
from home.serializers import SendOTPSerializer
from home.utils.otp import generate_otp, hash_otp


class SendPhoneOTP(APIView):
    permission_classes = []

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        otp = generate_otp()

        # Delete old OTP
        PhoneOTP.objects.filter(phone=phone).delete()

        PhoneOTP.objects.create(
            phone=phone,
            otp_hash=hash_otp(otp)
        )

       

        return Response(
            {"message": "OTP generated (check server console)"},
            status=status.HTTP_200_OK
        )
