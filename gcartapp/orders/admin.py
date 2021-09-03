from django.contrib import admin

from .models import Payment, Order, OrderProduct


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "payment_id",
        "payment_method",
        "amount_paid",
        "status",
        "created_at",
    )
    list_display_links = (
        "id",
        "user",
        "payment_id",
    )
    list_filter = [
        "user",
        "payment_method",
        "status",
    ]
    ordering = [
        "id",
    ]
    readonly_fields = ("id",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "payment",
        "order_number",
        "email",
        "order_total",
        "status",
        "is_ordered",
        "created_at",
    )
    list_display_links = (
        "id",
        "user",
        "payment",
    )
    list_filter = [
        "user",
        "status",
        "is_ordered",
        "created_at",
    ]
    ordering = [
        "id",
    ]
    readonly_fields = ("id",)


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "payment",
        "user",
        "product",
        "quantity",
        "product_price",
        "ordered",
        "created_at",
    )
    list_display_links = (
        "id",
        "order",
        "payment",
        "user",
    )
    list_filter = [
        "order",
        "payment",
        "user",
        "product",
        "quantity",
        "product_price",
        "ordered",
        "created_at",
    ]
    ordering = [
        "id",
    ]
    readonly_fields = ("id",)
