import shortuuid
from django.contrib import messages, auth
from django.shortcuts import redirect, render
from django.views.generic import base
from django.urls import reverse
from django.conf import settings

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from .forms import RegistrationForm
from cart.models import Cart, CartItem
from cart.views import get_session_id
from .tasks import send_mail_task
from orders.models import Order


class RegisterView(base.View):
    def get(self, request):
        form = RegistrationForm()
        context = {
            "form": form,
        }
        return render(request, "user/register.html", context)

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = (
                email.split("@")[0]
                + "-"
                + shortuuid.ShortUUID().random(length=6).upper()
            )
            user = auth.get_user_model().objects.create_user(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
            )

            # Email functionality
            current_site = get_current_site(request)
            mail_subject = "Please activate your account!"
            message = render_to_string(
                "user/user_verification_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            from_email = settings.SENDER_EMAIL
            # send_email = EmailMessage(
            #     mail_subject, message, to=[to_email], from_email=from_email
            # )
            # send_email.send()
            send_mail_task.delay(mail_subject, message, to_email, from_email)
            #

            return redirect(
                reverse("login") + "?command=verification&email=" + email
            )
        else:
            context = {
                "form": form,
            }
            return render(request, "user/register.html", context)


class ActivatePageView(base.View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = auth.get_user_model()._default_manager.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            auth.get_user_model().DoesNotExist,
        ):
            user = None

        if user is not None and default_token_generator.check_token(
            user, token
        ):
            user.is_active = True
            user.save()
            messages.success(
                request, "Congratulations! Your account is activated."
            )
            return redirect("login")
        else:
            messages.error(request, "Invalid activation link.")
            return redirect("register")


class LoginView(base.View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return render(request, "user/login.html")

    def post(self, request):
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=get_session_id(request))
                is_exists_cart_item = CartItem.objects.filter(
                    cart=cart
                ).exists()
                if is_exists_cart_item:
                    cart_item = CartItem.objects.filter(cart=cart)
                    for item in cart_item:
                        item.user = user
                        item.save()

            except Cart.DoesNotExist:
                pass

            auth.login(request, user)
            messages.success(request, "Login Successful!")

            try:
                cart_items = CartItem.objects.all().filter(user=request.user)
                if cart_items:
                    return redirect("cart")
                else:
                    return redirect("dashboard")
            except CartItem.DoesNotExist:
                return redirect("dashboard")
        else:
            messages.error(request, "Invalid Credentails!")
            return redirect("login")


class LogoutView(base.View):
    def get(self, request):
        if request.user.is_authenticated:
            auth.logout(request)
            messages.success(request, "You are logged out.")
            return redirect("login")
        else:
            messages.error(request, "You were not logged in!")
            return redirect("login")


class DashboardView(base.View):
    def get(self, request):
        if request.user.is_authenticated:
            order = Order.objects.order_by("-created_at").filter(
                user_id=request.user.id, is_ordered=True
            )
            order_count = order.count()
            context = {
                "order_count": order_count,
            }
            return render(request, "user/dashboard.html", context)
        else:
            messages.error(request, "You were not logged in!")
            return redirect("login")


class ForgotPasswordView(base.View):
    def get(self, request):
        return render(request, "user/forgot_password.html")

    def post(self, request):
        email = request.POST["email"]
        if auth.get_user_model().objects.filter(email=email).exists():
            user = auth.get_user_model().objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message = render_to_string(
                "user/reset_password_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            from_email = settings.SENDER_EMAIL
            send_email = EmailMessage(
                mail_subject, message, to=[to_email], from_email=from_email
            )
            send_email.send()

            messages.success(
                request,
                "Password reset email has been sent to your email address.",
            )
            return redirect("login")
        else:
            messages.error(request, "Account does not exist!")
            return redirect("forgotpassword")


class ResetPasswordValidateView(base.View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = auth.get_user_model()._default_manager.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            auth.get_user_model().DoesNotExist,
        ):
            user = None

        if user is not None and default_token_generator.check_token(
            user, token
        ):
            request.session["uid"] = uid
            messages.success(request, "Please reset your password.")
            return redirect("reset_password")
        else:
            messages.error(request, "This link has expired!")
            return redirect("login")


class ResetPasswordView(base.View):
    def post(self, request):
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password == confirm_password:
            uid = request.session.get("uid")
            user = auth.get_user_model().objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request, "Password do not match!")
            return redirect("reset_password")

    def get(self, request):
        return render(request, "user/reset_password.html")


class MyOrders(base.View):
    def get(self, request):
        if request.user.is_authenticated:
            orders = Order.objects.filter(
                user=request.user, is_ordered=True
            ).order_by("-created_at")
            context = {
                "orders": orders,
            }
            return render(request, "user/my_orders.html", context)
        else:
            messages.error(request, "Please login first.")
        return redirect("login")
