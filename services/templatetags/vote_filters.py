from django import template

register = template.Library()


@register.filter
def user_vote(comment, user):
    """Get the user's vote on a comment"""
    if not user or not user.is_authenticated:
        return None
    return comment.get_user_vote(user)
