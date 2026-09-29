from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Festival,WishLog

admin.site.register(Festival)
admin.site.register(WishLog)


