from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from unfold.admin import ModelAdmin
from django.contrib.auth.models import Group
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.safestring import mark_safe
import base64
from PIL import Image
from .models import User
# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    fieldsets = (
        (None, {'fields': ('user_code','phone', 'password', 'is_active')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Make this user an admin', {'fields': ('is_staff',)})
    )
    list_display = ['user_code','phone', 'display_qr_code']

    def display_qr_code(self, obj):
        if obj.user_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(obj.user_code)
            qr.make(fit=True)

            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return mark_safe(f'<img style="border-radius:10px;" id="qr-code-img" src="data:image/png;base64,{img_str}" width="150" height="150" />')
        return "No QR Code"

    display_qr_code.short_description = 'QR Code'
