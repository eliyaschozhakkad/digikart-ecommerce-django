# Generated by Django 4.1.3 on 2022-12-21 09:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("carts", "0004_cart_coupon"),
    ]

    operations = [
        migrations.RemoveField(model_name="cart", name="coupon",),
    ]
