# Generated by Django 4.1.3 on 2022-12-19 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("offers", "0004_alter_offer_category_alter_offer_product"),
    ]

    operations = [
        migrations.AddField(
            model_name="offer",
            name="is_valid",
            field=models.BooleanField(default=False),
        ),
    ]
