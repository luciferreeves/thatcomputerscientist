# Generated by Django 4.0.6 on 2022-11-22 06:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectDirectory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Object',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('md5', models.CharField(max_length=32)),
                ('metadata', models.CharField(max_length=255)),
                ('data', models.BinaryField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('location', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='ignis.objectdirectory')),
            ],
        ),
    ]