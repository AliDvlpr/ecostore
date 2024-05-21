# check_or_create_superuser.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Replace '1111' with the actual phone number attribute in your user model
if not User.objects.filter(phone='1111').exists():
    User.objects.create_superuser('1111', 'password')
