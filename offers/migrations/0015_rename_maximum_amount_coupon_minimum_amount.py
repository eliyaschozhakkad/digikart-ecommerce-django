# Generated by Django 4.1.3 on 2022-12-21 04:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("offers", "0014_coupon"),
    ]

    operations = [
        migrations.RenameField(
            model_name="coupon", old_name="maximum_amount", new_name="minimum_amount",
        ),
    ]
