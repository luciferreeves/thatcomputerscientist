# Generated by Django 4.1.4 on 2023-01-26 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0006_remove_post_post_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="body",
            field=models.TextField(blank=True),
        ),
    ]
