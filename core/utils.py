import random
import string

def generate_otp(length=5):
    characters = string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp