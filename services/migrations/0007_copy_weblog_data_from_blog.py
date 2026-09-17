from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0006_category_tag_post_comment_posttranslation_and_more"),
    ]

    operations = [
        migrations.RunPython(migrations.RunPython.noop, migrations.RunPython.noop),
    ]
