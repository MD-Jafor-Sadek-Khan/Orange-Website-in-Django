# Generated by Django 4.2.4 on 2023-09-08 21:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0004_product_sold"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="image1",
            field=models.ImageField(blank=True, upload_to="photos/products"),
        ),
        migrations.AddField(
            model_name="product",
            name="image2",
            field=models.ImageField(blank=True, upload_to="photos/products"),
        ),
        migrations.AddField(
            model_name="product",
            name="image3",
            field=models.ImageField(blank=True, upload_to="photos/products"),
        ),
        migrations.AddField(
            model_name="product",
            name="image4",
            field=models.ImageField(blank=True, upload_to="photos/products"),
        ),
    ]