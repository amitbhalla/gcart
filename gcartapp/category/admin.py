from django.contrib import admin

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug": ("category_name",),
    }
    list_display = (
        "category_name",
        "slug",
        "id",
    )
    list_display_links = (
        "category_name",
        "slug",
    )
    list_filter = [
        "category_name",
    ]
    ordering = [
        "id",
    ]
    readonly_fields = ("id",)
