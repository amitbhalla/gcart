from django.urls import path

from .views import PlaceOrderView

urlpatterns = [
    path(
        "place_order/",
        PlaceOrderView.as_view(),
        name="place_order",
    ),
]
