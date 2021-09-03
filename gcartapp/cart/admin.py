from django.contrib import admin

from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "cart_id",
        "date_added",
    )
    list_display_links = (
        "id",
        "cart_id",
    )
    list_filter = [
        "date_added",
    ]
    ordering = [
        "date_added",
    ]
    readonly_fields = ("id",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "quantity",
        "cart",
        "is_active",
    )
    list_display_links = (
        "id",
        "user",
        "product",
        "cart",
    )
    list_filter = [
        "product",
        "is_active",
    ]
    ordering = [
        "id",
    ]
    readonly_fields = ("id",)
