# Generated by Django 4.1.4 on 2023-03-26 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0009_post_post_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
