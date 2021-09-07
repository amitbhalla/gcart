import os
import uuid
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.db.models import Avg, Count

from category.models import Category

VARIATION_CATEGORY_CHOICE = (
    (
        "color",
        "color",
    ),
    (
        "size",
        "size",
    ),
)


def product_image(instance, filename):
    """Generate file path for a resource"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("images/products/", filename)


class Product(models.Model):
    product_name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to=product_image)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

    def get_url(self):
        return reverse("products_detail", args=[self.category.slug, self.slug])

    def averageReview(self):
        reviews = ReviewRating.objects.filter(
            product=self, status=True
        ).aggregate(average=Avg("rating"))
        avg = 0
        if reviews["average"] is not None:
            avg = float(reviews["average"])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(
            product=self, status=True
        ).aggregate(count=Count("id"))
        count = 0
        if reviews["count"] is not None:
            count = int(reviews["count"])
        return count


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(
            variation_category="color", is_active=True
        )

    def sizes(self):
        return super(VariationManager, self).filter(
            variation_category="size", is_active=True
        )


class Variation(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variations"
    )
    variation_category = models.CharField(
        max_length=255, choices=VARIATION_CATEGORY_CHOICE
    )
    variation_value = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    class Meta:
        ordering = ["variation_value"]

    def __str__(self):
        return str(self.variation_value)


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    subject = models.CharField(max_length=255, blank=True)
    review = models.TextField(blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=255, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
