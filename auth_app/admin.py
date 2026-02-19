from django.contrib import admin
from .models import UserProfile


class UserProfileExtension(admin.ModelAdmin):
    list_filter= ["id","user", "is_active"]
    list_display = ["id","user", "is_active"]
    readonly_fields = ["id", "is_active"]

admin.site.register(UserProfile, UserProfileExtension)