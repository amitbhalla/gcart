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
    def get(
        self, request, total=0, quantity=0, cart_items=None, cart_item=None
    ):

        try:
            cart = Cart.objects.get(cart_id=get_session_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

            for cart_item in cart_items:
                total += cart_item.product.price * cart_item.quantity
                quantity += cart_item.quantity

        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            pass

        context = {
            "total": total,
            "quantity": quantity,
            "cart_items": cart_items,
        }
        print(context)
        return render(request, "cart/cart.html", context)
