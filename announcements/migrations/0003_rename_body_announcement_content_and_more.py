# Generated by Django 4.0.6 on 2022-10-02 16:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('announcements', '0002_rename_date_announcement_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='announcement',
            old_name='body',
            new_name='content',
        ),
        migrations.RemoveField(
            model_name='announcement',
            name='title',
        ),
    ]
