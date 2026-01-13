from home.utils.twilio_otp import send_sms_otp

def send_otp(phone, otp):
    # single source of truth for OTP sending
    send_sms_otp(phone, otp)
