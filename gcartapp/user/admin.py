from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from django.utils.html import format_html

from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "last_login",
    )
    list_display_links = (
        "email",
        "username",
        "first_name",
        "last_name",
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
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": ("last_login",),
            },
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


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html(
            '<img src="{}" width="30" height="30" style="border-radius:50%;">'.format(
                object.profile_picture.url
            )
        )

    thumbnail.short_description = "Profile Picture"
    list_display = (
        "thumbnail",
        "user",
        "address_line_1",
        "address_line_2",
        "city",
        "state",
        "country",
        "id",
    )
    list_display_links = ("user", "id")
    list_filter = [
        "user",
    ]
    ordering = [
        "id",
    ]
    readonly_fields = ("id",)
