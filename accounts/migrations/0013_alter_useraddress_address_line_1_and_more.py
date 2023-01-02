# Generated by Django 4.1.3 on 2023-01-01 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0012_alter_useraddress_address_line_1_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="useraddress",
            name="address_line_1",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="useraddress",
            name="city",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name="useraddress",
            name="email",
            field=models.EmailField(max_length=100),
        ),
        migrations.AlterField(
            model_name="useraddress",
            name="first_name",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="useraddress",
            name="last_name",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="useraddress",
            name="phone_number",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="useraddress", name="pincode", field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="useraddress",
            name="state",
            field=models.CharField(max_length=20),
        ),
    ]
