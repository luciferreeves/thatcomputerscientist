# Generated by Django 4.0.6 on 2022-11-12 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcements', '0003_rename_body_announcement_content_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
