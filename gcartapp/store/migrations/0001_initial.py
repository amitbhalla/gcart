# Generated by Django 3.2.6 on 2021-09-05 12:29

from django.db import migrations, models
import django.db.models.deletion
import store.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "product_name",
                    models.CharField(max_length=255, unique=True),
                ),
                ("slug", models.SlugField(unique=True)),
                ("description", models.TextField(blank=True)),
                ("price", models.IntegerField()),
                (
                    "image",
                    models.ImageField(upload_to=store.models.product_image),
                ),
                ("stock", models.IntegerField()),
                ("is_available", models.BooleanField(default=True)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("modified_date", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Variation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "variation_category",
                    models.CharField(
                        choices=[("color", "color"), ("size", "size")],
                        max_length=255,
                    ),
                ),
                ("variation_value", models.CharField(max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("created_date", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="variations",
                        to="store.product",
                    ),
                ),
            ],
            options={
                "ordering": ["variation_value"],
            },
        ),
        migrations.CreateModel(
            name="ReviewRating",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subject", models.CharField(blank=True, max_length=255)),
                ("review", models.TextField(blank=True)),
                ("rating", models.FloatField()),
                ("ip", models.CharField(blank=True, max_length=255)),
                ("status", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="store.product",
                    ),
                ),
            ],
        ),
    ]
