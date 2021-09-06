from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import base
from django.core.paginator import Paginator
from django.db.models import Q
from django.http.response import Http404
from django.contrib import messages

from store.models import Product, ReviewRating
from category.models import Category
from .forms import ReviewForm


class StoreView(base.View):
    def get(self, request, category_slug=None):

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = Product.objects.filter(
                is_available=True, category=category
            ).order_by("-modified_date")
        else:
            products = Product.objects.filter(is_available=True).order_by(
                "-modified_date"
            )

        PAGINATION_NUMBER = 6
        paginator = Paginator(products, PAGINATION_NUMBER)
        page = request.GET.get("page")
        paged_products = paginator.get_page(page)
        products_count = products.count()
        if (products_count % PAGINATION_NUMBER) == 0:
            last_page = PAGINATION_NUMBER
        else:
            last_page = products_count % PAGINATION_NUMBER

        context = {
            "products": paged_products,
            "paged": PAGINATION_NUMBER,
            "last_page": last_page,
            "products_count": products_count,
        }
        return render(request, "store/store.html", context)


class ProductView(base.View):
    def get(self, request, category_slug=None, product_slug=None):
        category = get_object_or_404(Category, slug=category_slug)
        product = get_object_or_404(
            Product, category=category, slug=product_slug
        )

        context = {
            "product": product,
        }
        return render(request, "store/product_detail.html", context)


class SearchPageView(base.View):
    def get(self, request):

        products = []
        product_count = 0
        if "keyword" in request.GET:
            searched_term = request.GET["keyword"]
            if searched_term:
                try:
                    products = Product.objects.filter(
                        Q(description__icontains=searched_term)
                        | Q(product_name__icontains=searched_term),
                        is_available=True,
                    ).order_by("-modified_date")
                    product_count = products.count()
                except Product.DoesNotExist:
                    return Http404()

        paginator = Paginator(products, 6)
        page = request.GET.get("page")
        paged_products = paginator.get_page(page)
        context = {
            "products": paged_products,
            "product_count": product_count,
        }

        return render(request, "store/store.html", context)


class SubmitReviewView(base.View):
    def post(self, request, product_id):
        url = request.META.get("HTTP_REFERER")
        try:
            reviews = ReviewRating.objects.get(
                user__id=request.user.id, product__id=product_id
            )
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(
                request, "Thank you! Your review has been updated."
            )
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data["subject"]
                data.rating = form.cleaned_data["rating"]
                data.review = form.cleaned_data["review"]
                data.ip = request.META.get("REMOTE_ADDR")
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(
                    request, "Thank you! Your review has been submitted."
                )
                return redirect(url)
