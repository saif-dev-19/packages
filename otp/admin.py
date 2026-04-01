from django.contrib import admin

from otp.models import OTP

# Register your models here.
admin.site.site_header = "OTP Management"
admin.site.site_title = "OTP Admin"
admin.site.index_title = "Manage OTPs"
admin.site.register(OTP)