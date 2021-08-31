from django.shortcuts import render
from django.views.generic import base

from store.models import Product


class CartView(base.View):
    def get(self, request):
        context = {
            "products": "cart",
        }
        return render(request, "cart/cart.html", context)
