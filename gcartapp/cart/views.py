from math import prod
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import base

from store.models import Product, Variation
from .models import Cart, CartItem


def get_session_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


class AddCartView(base.View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product_variation = []
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

        try:
            cart = Cart.objects.get(cart_id=get_session_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=get_session_id(request))
            cart.save()

        # check if we have any cart items
        if request.user.is_authenticated:
            is_exists_cart_item = CartItem.objects.filter(
                product=product,
                user=request.user,
            ).exists()
        else:
            is_exists_cart_item = CartItem.objects.filter(
                product=product,
                cart=cart,
            ).exists()

        if is_exists_cart_item:

            if request.user.is_authenticated:
                cart_item = CartItem.objects.filter(
                    product=product,
                    user=request.user,
                )
            else:
                cart_item = CartItem.objects.filter(
                    product=product,
                    cart=cart,
                )
            existing_variation_list = []
            id_list = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id_list.append(item.id)

            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                item_id = id_list[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                if request.user.is_authenticated:
                    item.user = request.user
                item.save()
            else:
                if request.user.is_authenticated:
                    cart_item = CartItem.objects.create(
                        product=product,
                        quantity=1,
                        cart=cart,
                        user=request.user,
                    )
                else:
                    cart_item = CartItem.objects.create(
                        product=product, quantity=1, cart=cart
                    )
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()
        else:
            if request.user.is_authenticated:
                cart_item = CartItem.objects.create(
                    product=product, cart=cart, quantity=1, user=request.user
                )
            else:
                cart_item = CartItem.objects.create(
                    product=product,
                    cart=cart,
                    quantity=1,
                )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect("cart")


class RemoveCartView(base.View):
    def post(self, request, product_id, cart_item_id):
        product = Product.objects.get(id=product_id)
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                user=request.user, product=product, id=cart_item_id
            )
        else:
            cart = Cart.objects.get(cart_id=get_session_id(request))
            cart_item = CartItem.objects.get(
                cart=cart, product=product, id=cart_item_id
            )

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

        return redirect("cart")


class RemoveCartItemView(base.View):
    def post(self, request, product_id, cart_item_id):
        product = Product.objects.get(id=product_id)
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                user=request.user, product=product
            )
        else:
            cart = Cart.objects.get(cart_id=get_session_id(request))
            cart_item = CartItem.objects.get(
                cart=cart, product=product, id=cart_item_id
            )
        cart_item.delete()
        return redirect("cart")


class CartView(base.View):
    def get(
        self,
        request,
        total=0.0,
        quantity=0,
        cart_items=None,
        cart_item=None,
        tax_percentage=0.02,
        tax=0.0,
        grand_total=0.0,
    ):

        try:
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart = Cart.objects.get(cart_id=get_session_id(request))
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)

            for cart_item in cart_items:
                total += cart_item.product.price * cart_item.quantity
                quantity += cart_item.quantity

            tax = total * tax_percentage
            grand_total = total + tax

        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            pass

        context = {
            "total": total,
            "quantity": quantity,
            "cart_items": cart_items,
            "tax": tax,
            "grand_total": grand_total,
        }
        return render(request, "cart/cart.html", context)


class CheckoutView(base.View):
    def get(
        self,
        request,
        total=0.0,
        quantity=0,
        cart_items=None,
        cart_item=None,
        tax_percentage=0.02,
        tax=0.0,
        grand_total=0.0,
    ):
        if request.user.is_authenticated:
            try:
                cart = Cart.objects.get(cart_id=get_session_id(request))
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)

                for cart_item in cart_items:
                    total += cart_item.product.price * cart_item.quantity
                    quantity += cart_item.quantity

                tax = total * tax_percentage
                grand_total = total + tax

            except (Cart.DoesNotExist, CartItem.DoesNotExist):
                pass

            context = {
                "total": total,
                "quantity": quantity,
                "cart_items": cart_items,
                "tax": tax,
                "grand_total": grand_total,
            }
            return render(request, "cart/checkout.html", context)
        else:
            messages.error(request, "Please login to checkout.")
            return redirect("login")
