from django.urls import path

from .views import StoreView

urlpatterns = [
    path("", StoreView.as_view(), name="store"),
    path(
        "<slug:category_slug>/",
        StoreView.as_view(),
        name="products_by_category",
    ),
]
