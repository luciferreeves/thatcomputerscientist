from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_alter_anonymouscommentuser_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anonymouscommentuser',
            name='email',
            field=models.CharField(max_length=254, unique=True, verbose_name='Email'),
        ),
    ]
