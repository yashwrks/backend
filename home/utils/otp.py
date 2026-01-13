import random
from django.contrib.auth.hashers import make_password, check_password

def generate_otp():
    return str(random.randint(100000, 999999))

def hash_otp(otp):
    return make_password(otp)

def verify_otp(otp, hashed):
    return check_password(otp, hashed)
