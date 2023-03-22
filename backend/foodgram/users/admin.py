from django.contrib import admin
from .models import CustomUser, Follow


@admin.register(CustomUser)
class CustomUserAdmit(admin.ModelAdmin):
    """Admin model for CustomUser."""

    list_filter = ('username', 'email', )


admin.site.register(Follow)
