from django.shortcuts import render, get_object_or_404
from django.views.generic import base

from store.models import Product
from category.models import Category
from cart.models import CartItem
from cart.views import get_session_id


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
        category = get_object_or_404(Category, slug=category_slug)
        product = get_object_or_404(
            Product, category=category, slug=product_slug
        )
        in_cart = CartItem.objects.filter(
            cart__cart_id=get_session_id(request),
            product__slug=product_slug,
        ).exists()

        context = {
            "in_cart": in_cart,
            "product": product,
        }
        return render(request, "store/product_detail.html", context)
