# Generated by Django 3.2.6 on 2021-09-04 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0004_alter_order_order_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="signature",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]