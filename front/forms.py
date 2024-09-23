from django import forms
from django.core.exceptions import ValidationError
from core.models import User
from store.models import Customer

class LoginForm(forms.Form):
    phone = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "phone number",
        "required": "required",
        "data-validation-required-message": "Please enter your phone number",
    }))

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit() or len(phone) <= 3:
            raise ValidationError("Phone number must be a number with more than 3 digits.")
        return phone

class OTPForm(forms.Form):
    otp = forms.CharField(widget=forms.TextInput(attrs={
         "type":"",
         "class":"form-control",
         "placeholder":"verify token",
         "required":"required",
         "data-validation-required-message":"Please enter your verify token",
    }))

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'user_code']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'user_code': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

class CustomerProfileForm(forms.Form):
    class Meta:
        model = Customer
        fields = ['name', 'telegram_id']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'telegram_id': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }