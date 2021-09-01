from django.shortcuts import render
from django.views.generic import base

from .forms import RegistrationForm


class RegisterView(base.View):
    def get(self, request):

        form = RegistrationForm()
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
