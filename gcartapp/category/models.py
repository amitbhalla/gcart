import os
import uuid
from django.db import models


def category_image(instance, filename):
    """Generate file path for a resource"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("images/categories/", filename)


class Category(models.Model):
    category_name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True)
    cat_image = models.ImageField(upload_to=category_image, blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name
