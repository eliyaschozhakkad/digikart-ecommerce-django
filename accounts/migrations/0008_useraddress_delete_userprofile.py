# Generated by Django 4.1.3 on 2022-12-17 06:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_userprofile_email_userprofile_phone_number"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserAddress",
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
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("address_line_1", models.CharField(blank=True, max_length=100)),
                ("address_line_2", models.CharField(blank=True, max_length=100)),
                (
                    "profile_picture",
                    models.ImageField(blank=True, null=True, upload_to="userprofile"),
                ),
                ("city", models.CharField(blank=True, max_length=20)),
                ("state", models.CharField(blank=True, max_length=20)),
                ("pincode", models.IntegerField(blank=True)),
                ("email", models.EmailField(blank=True, max_length=100)),
                ("phone_number", models.CharField(blank=True, max_length=50)),
                (
                    "add_type",
                    models.CharField(
                        choices=[("Home", "Home"), ("Word", "Work")], max_length=50
                    ),
                ),
                ("default", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(name="UserProfile",),
    ]
