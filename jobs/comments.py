from celery import shared_task
from django.db import transaction
from services.weblog.models import Comment
from internal.weblog_utilities import check_comment_spam
import logging

logger = logging.getLogger(__name__)


def _process_single_comment(comment):
    spam_result = check_comment_spam(comment=comment.body, post=comment.post)
    
    if spam_result == "N":
        comment.approve_comment()
        return "approved"
    else:
        comment.delete()
        return "deleted as spam"


@shared_task(bind=True, max_retries=3)
def check_comment_spam_async(self, comment_id):
    try:
        with transaction.atomic():
            try:
                comment = Comment.objects.select_for_update().get(id=comment_id)
            except Comment.DoesNotExist:
                return f"Comment {comment_id} not found"

            if comment.spam_status != "pending":
                return f"Comment {comment_id} already processed"

            result = _process_single_comment(comment)
            return f"Comment {comment_id} processed: {result}"

    except Exception as exc:
        logger.error(f"Error processing comment {comment_id}: {type(exc).__name__}: {str(exc)}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2**self.request.retries))
        else:
            try:
                comment = Comment.objects.get(id=comment_id)
                if comment.spam_status == "pending":
                    comment.approve_comment()
            except:
                pass
            return f"Comment {comment_id} auto-approved after failed spam check"


def queue_spam_check(comment_id: int) -> None:
    """Enqueue the asynchronous spam check for a comment."""
    from thatcomputerscientist.celery import app

    app.send_task("jobs.comments.check_comment_spam_async", args=[comment_id])


@shared_task
def process_pending_and_spam_comments():
    processed_count = 0
    deleted_count = 0

    manually_spam_comments = Comment.objects.filter(spam_status="spam")
    for comment in manually_spam_comments:
        comment.delete()
        deleted_count += 1

    pending_comments = Comment.objects.filter(spam_status="pending")
    for comment in pending_comments:
        try:
            result = _process_single_comment(comment)
            if result == "deleted as spam":
                deleted_count += 1
            processed_count += 1
        except Exception as e:
            logger.error(f"Error processing comment {comment.id}: {e}")
            comment.approve_comment()
            processed_count += 1

    return f"Processed {processed_count} pending comments, deleted {deleted_count} spam comments"