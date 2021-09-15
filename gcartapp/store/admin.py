import admin_thumbnails
from django.contrib import admin

from .models import Product, Variation, ReviewRating, ProductGallery


@admin_thumbnails.thumbnail("image")
class ProdGallaryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


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
    list_filter = [
        "category",
        "is_available",
    ]
    ordering = [
        "id",
    ]
    readonly_fields = ("id",)
    inlines = [ProdGallaryInline]


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "variation_category",
        "variation_value",
        "is_active",
        "created_date",
    )
    list_display_links = (
        "id",
        "product",
    )
    list_editable = [
        "is_active",
    ]
    list_filter = [
        "is_active",
        "product",
    ]
    ordering = [
        "id",
    ]
    readonly_fields = ("id",)


@admin.register(ReviewRating)
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "user",
        "subject",
        "review",
        "rating",
        "ip",
        "status",
    )
    list_display_links = (
        "id",
        "product",
        "user",
    )
    list_editable = [
        "subject",
        "rating",
        "status",
    ]
    list_filter = [
        "status",
        "product",
        "user",
    ]
    ordering = [
        "id",
    ]
    readonly_fields = ("id",)


@admin.register(ProductGallery)
class ProductGalleryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
    )
    list_display_links = (
        "id",
        "product",
    )

    list_filter = [
        "product",
    ]
    ordering = [
        "id",
    ]
    readonly_fields = ("id",)
