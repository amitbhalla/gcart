import shortuuid
from django.contrib import messages, auth
from django.shortcuts import redirect, render
from django.views.generic import base

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from .forms import RegistrationForm
from .models import User


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
            from_email = "Django@bcg.com"
            send_email = EmailMessage(
                mail_subject, message, to=[to_email], from_email=from_email
            )
            send_email.send()
            #

            messages.success(
                request, "Registration Successful. Please check your email."
            )
            context = {
                "form": form,
            }
            return render(request, "user/register.html", context)
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
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
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
        return render(request, "user/login.html")

    def post(self, request):
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            # messages.success(request, "Login Successful!")
            return redirect("home")
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
