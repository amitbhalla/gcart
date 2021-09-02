import shortuuid
from django.shortcuts import render
from django.views.generic import base
from django.contrib.auth import get_user_model

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
            user = get_user_model().objects.create_user(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
            )
            context = {
                "form": form,
            }
            return render(request, "user/register.html", context)


class LoginView(base.View):
    def get(self, request):
        context = {}
        return render(request, "user/login.html")


class LogoutView(base.View):
    pass
