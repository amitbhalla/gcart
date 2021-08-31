from django.shortcuts import render
from django.views.generic import base

from store.models import Product


class StoreView(base.View):
    def get(self, request):
        products = Product.objects.filter(is_available=True).order_by(
            "-modified_date"
        )
        context = {
            "products": products,
        }
        return render(request, "store/store.html", context)
