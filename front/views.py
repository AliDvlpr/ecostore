from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_protect
from core.models import User
from core.utils import generate_otp
from .forms import LoginForm, OTPForm

def home(request):
    return render(request, 'front/home.html')

@login_required(login_url='/login/')
def profile(request):
    return render(request, 'front/profile.html')

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                user = User(phone=phone, username=phone)
                user.save()

            otp = generate_otp()
            user.otp = otp
            user.save()

            return redirect('verify_otp', phone=phone)
    else:
        form = LoginForm()
    return render(request, 'front/login.html', {'form': form})

@csrf_protect
def verify_otp(request, phone):
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_received = form.cleaned_data['otp']
            if user.otp == otp_received:
                login(request, user)
                user.otp = None
                user.save()
                return redirect('profile')
            else:
                form.add_error('otp', 'Invalid OTP')
    else:
        form = OTPForm()
    return render(request, 'front/verify_otp.html', {'form': form, 'phone': phone})