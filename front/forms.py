from django import forms

class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15)

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)
