from django.contrib.auth.models import User
from haystack import indexes

from apps.blog.models import Comment, Post


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr="title")
    body = indexes.CharField(model_attr="body")
    date = indexes.DateTimeField(model_attr="date")

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        """Return all published posts."""
        return self.get_model().objects.filter(is_public=True)


class UserIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    username = indexes.CharField(model_attr="username")
    first_name = indexes.CharField(model_attr="first_name")
    last_name = indexes.CharField(model_attr="last_name")
    email = indexes.CharField(model_attr="email")

    def get_model(self):
        return User

    def index_queryset(self, using=None):
        """Return all user profiles without filtering."""
        return self.get_model().objects.all()


class CommentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    post = indexes.CharField(model_attr="post")
    user = indexes.CharField(model_attr="user")
    body = indexes.CharField(model_attr="body")
    created_at = indexes.DateTimeField(model_attr="created_at")
    edited = indexes.BooleanField(model_attr="edited")
    edited_at = indexes.DateTimeField(model_attr="edited_at")

    def get_model(self):
        return Comment

    def index_queryset(self, using=None):
        """Return all comments without filtering."""
        return self.get_model().objects.all()
