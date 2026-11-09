from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0004_anonymouscommentuser_alter_userprofile_options"),
    ]

    operations = [
        migrations.RunPython(migrations.RunPython.noop, migrations.RunPython.noop),
    ]
