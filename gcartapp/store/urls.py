from django.urls import path

from .views import StoreView, ProductView, SearchPageView, SubmitReviewView

urlpatterns = [
    path(
        "search/",
        SearchPageView.as_view(),
        name="search",
    ),
    path(
        "submit_review/<int:product_id>",
        SubmitReviewView.as_view(),
        name="submit_review",
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
