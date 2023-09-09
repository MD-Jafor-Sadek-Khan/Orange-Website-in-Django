# Generated by Django 4.2.4 on 2023-09-09 16:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0007_alter_product_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="image1",
            field=models.ImageField(
                default="default/default_image1.jpg", upload_to="photos/products"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="image2",
            field=models.ImageField(
                default="default/default_image2.jpg", upload_to="photos/products"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="image3",
            field=models.ImageField(
                default="default/default_image3.jpg", upload_to="photos/products"
            ),
        ),
    ]
