# Generated by Django 4.0.6 on 2022-11-22 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_post_post_image'),
        ('ignis', '0009_rename_repositorytitles_repositorytitle_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postimage',
            name='post',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.post'),
        ),
    ]