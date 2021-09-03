import datetime as dt
from django.views.generic import base
from django.contrib import messages
from django.shortcuts import render, redirect

from cart.models import CartItem
from .forms import OrderForm
from .models import Order
from cart.views import TAX_PERCENTAGE


class PlaceOrderView(base.View):
    def get(self, request):
        if request.user.is_authenticated:
            current_user = request.user
            cart_items = CartItem.objects.filter(user=current_user)
            cart_count = cart_items.count()
            if cart_count == 0:
                return redirect("store")
            else:
                pass
        else:
            messages.error(
                request, "You need to login to perform this action."
            )
            return redirect("login")

    def post(self, request):
        if request.user.is_authenticated:
            current_user = request.user
            cart_items = CartItem.objects.filter(user=current_user)
            cart_count = cart_items.count()
            form = OrderForm(request.POST)
            if cart_count > 0:
                total = 0
                tax = 0
                quantity = 0
                for cart_item in cart_items:
                    total += cart_item.product.price * cart_item.quantity
                    quantity += cart_item.quantity
                tax = total * TAX_PERCENTAGE
                grand_total = total + tax

                if form.is_valid():
                    data = Order()
                    data.first_name = form.cleaned_data["first_name"]
                    data.last_name = form.cleaned_data["last_name"]
                    data.phone = form.cleaned_data["phone"]
                    data.email = form.cleaned_data["email"]
                    data.address_line_1 = form.cleaned_data["address_line_1"]
                    data.address_line_2 = form.cleaned_data["address_line_2"]
                    data.city = form.cleaned_data["city"]
                    data.state = form.cleaned_data["state"]
                    data.country = form.cleaned_data["country"]
                    data.order_note = form.cleaned_data["order_note"]
                    data.order_total = grand_total
                    data.tax = tax
                    data.ip = request.META.get("REMOTE_ADDR")
                    data.save()

                    context = {
                        "order": data,
                        "cart_items": cart_items,
                        "total": total,
                        "tax": tax,
                        "grand_total": grand_total,
                    }
                    return render(request, "orders/payments.html", context)
            else:
                return redirect("store")
        else:
            messages.error(
                request, "You need to login to perform this action."
            )
            return redirect("login")


class PaymentsView(base.View):
    def get(self, request):
        return render(request, "orders/payments.html")
