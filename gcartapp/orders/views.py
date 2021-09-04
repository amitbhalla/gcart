import datetime as dt
import razorpay
import json
from django.views.generic import base
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from cart.models import CartItem
from .forms import OrderForm
from .models import Order, Payment
from cart.views import TAX_PERCENTAGE


def razorpay_setup(amount, currency, receipt):
    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_ID,
            settings.RAZORPAY_SECRET,
        )
    )
    data = {
        "amount": amount,
        "currency": currency,
        "receipt": receipt,
    }
    payment = client.order.create(data=data)
    return payment


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
                    data.user = request.user
                    data.save()
                    amount = int(data.order_total) * 100
                    currency = "INR"
                    receipt = str(data.order_number)
                    payment = razorpay_setup(amount, currency, receipt)

                    context = {
                        "order": data,
                        "cart_items": cart_items,
                        "total": total,
                        "tax": tax,
                        "grand_total": grand_total,
                        "key": settings.RAZORPAY_ID,
                        "amount": payment["amount"],
                        "currency": payment["currency"],
                        "name": data.full_name,
                        "description": data.order_note,
                        "image": "",
                        "order_id": payment["id"],
                        "email": data.email,
                        "contact": data.phone,
                        "address": data.full_address,
                        "payment_method": "RazorPay",
                        "order_number": data.order_number,
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
    def post(self, request):
        body = json.loads(request.body)
        print("*" * 100)
        print(body["order"])
        print("*" * 100)
        try:
            order = Order.objects.get(
                user=request.user, is_ordered=False, order_number=body["order"]
            )
        except:
            pass
        print("*" * 100)
        print(order.order_total)
        print("*" * 100)
        payment = Payment.objects.create(
            user=request.user,
            payment_id=body["transID"],
            payment_method=body["paymentMethod"],
            amount_paid=order.order_total,
            status=body["status"],
            signature=body["signature"],
            signature_code=body["orderID"],
        )
        payment.save()
