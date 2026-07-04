from django.db import migrations


def backfill_self_upvotes(apps, schema_editor):
    Comment = apps.get_model("blog", "Comment")
    CommentVote = apps.get_model("blog", "CommentVote")

    for comment in Comment.objects.filter(user__isnull=False).iterator():
        CommentVote.objects.get_or_create(
            comment=comment,
            user_id=comment.user_id,
            defaults={"vote_type": 1},
        )
        upvotes = CommentVote.objects.filter(comment=comment, vote_type=1).count()
        downvotes = CommentVote.objects.filter(comment=comment, vote_type=-1).count()
        Comment.objects.filter(pk=comment.pk).update(upvotes=upvotes, downvotes=downvotes)


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0023_comment_spam_checked_at_comment_spam_status"),
    ]

    operations = [
        migrations.RunPython(backfill_self_upvotes, migrations.RunPython.noop),
    ]
