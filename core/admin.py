from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            (None, {'fields': ('phone', 'password', 'is_active')}),
            ('Personal info', {'fields': ('username', 'first_name', 'last_name')}),
            ('Make this user an admin', {'fields': ('is_staff',)})
        ),
    )
    list_display = ['phone']