from django.urls import path

from .views import CartView, AddCartView

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("add_cart/<int:product_id>/", AddCartView.as_view(), name="add_cart"),
]
