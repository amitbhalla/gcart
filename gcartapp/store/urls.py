from django.urls import path

from .views import StoreView, ProductView, SearchPage

urlpatterns = [
    path(
        "store/search/",
        SearchPage.as_view(),
        name="search",
    ),
    path(
        "<slug:category_slug>/<slug:product_slug>/",
        ProductView.as_view(),
        name="products_detail",
    ),
    path(
        "<slug:category_slug>/",
        StoreView.as_view(),
        name="products_by_category",
    ),
    path(
        "",
        StoreView.as_view(),
        name="store",
    ),
]
