from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import base

from store.models import Product
from .models import Cart, CartItem


def get_session_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


class AddCartView(base.View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        try:
            cart = Cart.objects.get(cart_id=get_session_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=get_session_id(request))
            cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product, cart=cart, quantity=1
            )
        cart_item.save()
        return redirect("cart")


class CartView(base.View):
    def get(self, request):
        context = {
            "products": "cart",
        }
        return render(request, "cart/cart.html", context)
