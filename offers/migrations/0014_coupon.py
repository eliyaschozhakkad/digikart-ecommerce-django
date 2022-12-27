# Generated by Django 4.1.3 on 2022-12-21 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("offers", "0013_remove_offer_is_valid"),
    ]

    operations = [
        migrations.CreateModel(
            name="Coupon",
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
                ("coupon_name", models.CharField(max_length=15, null=True)),
                ("coupon_code", models.CharField(max_length=10, null=True)),
                ("maximum_amount", models.IntegerField(null=True)),
                ("coupon_discount", models.IntegerField(null=True)),
            ],
        ),
    ]