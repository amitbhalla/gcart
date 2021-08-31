from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug": ("product_name",),
    }
    list_display = (
        "product_name",
        "price",
        "stock",
        "category",
        "slug",
        "is_available",
        "id",
    )
    list_display_links = (
        "product_name",
        "id",
    )
    list_editable = [
        "price",
        "stock",
        "is_available",
    ]
    ordering = [
        "id",
    ]
    readonly_fields = ("id",)
