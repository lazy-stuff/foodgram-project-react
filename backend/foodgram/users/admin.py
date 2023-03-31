from django.contrib import admin

from .models import CustomUser, Follow


@admin.register(CustomUser)
class CustomUserAdmit(admin.ModelAdmin):
    """Admin model for CustomUser."""

    list_filter = ('username', 'email', )


@admin.register(Follow)
class FollowAdmit(admin.ModelAdmin):
    """Admin model for Follow."""

    list_display = ('author', 'user', )
    list_filter = ('author', )
