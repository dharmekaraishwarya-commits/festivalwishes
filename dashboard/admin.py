from django.contrib import admin

# Register your models here.
from .models import AdminUser


admin.site.register(AdminUser)