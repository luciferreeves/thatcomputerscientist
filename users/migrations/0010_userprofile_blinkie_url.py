# Generated by Django 4.1.4 on 2023-04-04 01:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0009_delete_captchastore"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="blinkie_url",
            field=models.TextField(blank=True, default=""),
        ),
    ]