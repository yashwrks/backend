from django.urls import path
from home.views.otp import SendPhoneOTP
from home.views.login_otp import LoginSendOTP
from home.views.auth import SignupView, VerifyPhoneOTP
from home.views.dashboard import DashboardView
from home.views.call import start_call



from home.views.twilio_voice import twilio_voice
from home.views.forgot_password import (
    ForgotPasswordSendOTP,
    VerifyForgotPasswordOTP,
    ResetPassword
)

urlpatterns = [
    # 🔐 SIGNUP FLOW
    path("auth/signup/", SignupView.as_view()),          
    path("auth/send-otp/", SendPhoneOTP.as_view()),      

    # 🔑 LOGIN FLOW
    path("auth/login-otp/", LoginSendOTP.as_view()),     

    # ✅ VERIFY (COMMON FOR SIGNUP + LOGIN)
    path("auth/verify-otp/", VerifyPhoneOTP.as_view()),
    path("auth/forgot-password/", ForgotPasswordSendOTP.as_view()),
    path("auth/verify-forgot-otp/", VerifyForgotPasswordOTP.as_view()),
    path("auth/reset-password/", ResetPassword.as_view()),

    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    
    # 📞 CALL ROUTES
    path("call/start/", start_call),
    path("twilio/voice/", twilio_voice),
     # <-- AI speech processing
]
