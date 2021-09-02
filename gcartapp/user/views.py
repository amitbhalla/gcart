from django.contrib import messages, auth
import shortuuid
from django.shortcuts import redirect, render
from django.views.generic import base

from .forms import RegistrationForm


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
    pass
