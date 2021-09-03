from django.urls import path

from .views import PlaceOrderView, PaymentsView

urlpatterns = [
    path(
        "place_order/",
        PlaceOrderView.as_view(),
        name="place_order",
    ),
    path(
        "payments/<str:order_number>/",
        PaymentsView.as_view(),
        name="payments",
    ),
]
