# Generated by Django 3.2.6 on 2021-09-04 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0007_auto_20210904_1232"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderproduct",
            name="color",
        ),
        migrations.RemoveField(
            model_name="orderproduct",
            name="size",
        ),
    ]
