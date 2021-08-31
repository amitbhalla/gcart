from django.shortcuts import render, get_object_or_404
from django.views.generic import base

from store.models import Product
from category.models import Category


class StoreView(base.View):
    def get(self, request, category_slug=None):

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = Product.objects.filter(
                is_available=True, category=category
            ).order_by("-modified_date")
        else:
            products = Product.objects.filter(is_available=True).order_by(
                "-modified_date"
            )
        context = {
            "products": products,
            "products_count": products.count(),
        }
        return render(request, "store/store.html", context)


class ProductView(base.View):
    def get(self, request, category_slug=None, product_slug=None):
        product = get_object_or_404(Product, slug=product_slug)
        context = {"product": product}
        return render(request, "store/product_detail.html", context)
