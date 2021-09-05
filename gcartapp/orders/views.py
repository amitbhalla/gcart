import razorpay
import json
from django.views.generic import base
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.template.loader import render_to_string

from cart.models import CartItem
from store.models import Product
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from cart.views import TAX_PERCENTAGE
from user.tasks import send_mail_task


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

        if body["status"] == "Completed":
            order = Order.objects.get(
                user=request.user, is_ordered=False, order_number=body["order"]
            )
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
            order.payment = payment
            order.status = body["status"]
            order.is_ordered = True
            order.save()

            # Move the cart items to Order Product table
            cart_items = CartItem.objects.filter(user=request.user)

            for item in cart_items:
                #
                # Move cart items to Order Product
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.payment = payment
                orderproduct.user_id = request.user.id
                orderproduct.product_id = item.product_id
                orderproduct.quantity = item.quantity
                orderproduct.product_price = item.product.price
                orderproduct.ordered = True
                orderproduct.save()
                #
                # Save Variations
                cart_item = CartItem.objects.get(id=item.id)
                product_variation = cart_item.variations.all()
                orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                orderproduct.variations.set(product_variation)
                orderproduct.save()
                #
                # Reduce the quantity of the sold products
                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()

            # Clear Cart
            CartItem.objects.filter(user=request.user).delete()

            # Send order recieved email to customer
            mail_subject = "Thank you for your order!"
            message = render_to_string(
                "orders/order_recieved_email.html",
                {
                    "user": request.user,
                    "order": order,
                },
            )
            to_email = request.user.email
            from_email = settings.SENDER_EMAIL
            send_mail_task.delay(mail_subject, message, to_email, from_email)

            data = {
                "order_number": order.order_number,
                "transID": payment.payment_id,
            }
            return JsonResponse(data)


class OrderCompleteView(base.View):
    def get(self, request):
        order_number = request.GET.get("order_number")
        transID = request.GET.get("payment_id")
        try:
            order = Order.objects.get(
                order_number=order_number, is_ordered=True
            )
            ordered_products = OrderProduct.objects.filter(order_id=order.id)
            subtotal = 0
            for i in ordered_products:
                subtotal += i.product_price * i.quantity

            payment = Payment.objects.get(payment_id=transID)

            context = {
                "order": order,
                "ordered_products": ordered_products,
                "order_number": order.order_number,
                "transID": payment.payment_id,
                "payment": payment,
                "subtotal": subtotal,
            }
            return render(request, "orders/order_complete.html", context)
        except (Payment.DoesNotExist, Order.DoesNotExist):
            return redirect("home")
