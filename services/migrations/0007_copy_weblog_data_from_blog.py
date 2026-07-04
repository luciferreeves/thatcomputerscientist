from django.db import migrations

# Copied in FK-safe order: parents before children.
MODELS = [
    "Weblog",
    "Category",
    "Tag",
    "Post",
    "CategoryTranslation",
    "TagTranslation",
    "PostTranslation",
    "Comment",
    "CommentVote",
]


def _columns(connection, model):
    return ", ".join(
        connection.ops.quote_name(field.column)
        for field in model._meta.concrete_fields
    )


def copy_forward(apps, schema_editor):
    connection = schema_editor.connection
    quote = connection.ops.quote_name
    with connection.cursor() as cursor:
        for name in MODELS:
            source = apps.get_model("blog", name)
            target = apps.get_model("services", name)
            columns = _columns(connection, target)
            # Comments carry a self-referential parent FK: insert lower levels first.
            order = " ORDER BY level" if name == "Comment" else ""
            cursor.execute(
                f"INSERT INTO {quote(target._meta.db_table)} ({columns}) "
                f"SELECT {columns} FROM {quote(source._meta.db_table)}{order}"
            )

        source_through = apps.get_model("blog", "Post")._meta.get_field("tags").remote_field.through
        target_through = apps.get_model("services", "Post")._meta.get_field("tags").remote_field.through
        through_columns = _columns(connection, target_through)
        cursor.execute(
            f"INSERT INTO {quote(target_through._meta.db_table)} ({through_columns}) "
            f"SELECT {through_columns} FROM {quote(source_through._meta.db_table)}"
        )


def copy_reverse(apps, schema_editor):
    connection = schema_editor.connection
    quote = connection.ops.quote_name
    with connection.cursor() as cursor:
        target_through = apps.get_model("services", "Post")._meta.get_field("tags").remote_field.through
        cursor.execute(f"DELETE FROM {quote(target_through._meta.db_table)}")
        for name in reversed(MODELS):
            target = apps.get_model("services", name)
            cursor.execute(f"DELETE FROM {quote(target._meta.db_table)}")


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0006_category_tag_post_comment_posttranslation_and_more"),
        ("blog", "0024_backfill_comment_self_upvotes"),
    ]

    operations = [
        migrations.RunPython(copy_forward, copy_reverse),
    ]
