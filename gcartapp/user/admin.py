from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "username",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "last_login",
    )
    ordering = [
        "email",
    ]
    readonly_fields = ("id",)
    list_filter = [
        "is_active",
        "is_staff",
        "is_superuser",
    ]
    list_editable = [
        "is_active",
        "is_staff",
        "is_superuser",
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                    "username",
                )
            },
        ),
        (
            _("Personal Info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                )
            },
        ),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
