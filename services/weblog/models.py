from bs4 import BeautifulSoup
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import get_language, gettext_lazy as _
from core.translations import TranslatableMixin, Translation

UPLOAD_ROOT = "images/"

SPAM_STATUS_CHOICES = [
    ("pending", _("Pending Review")),
    ("approved", _("Approved")),
    ("spam", _("Marked as Spam")),
]


class CategoryTranslation(Translation):
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, related_name="translations", verbose_name=_("Category")
    )
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        unique_together = ["category", "language"]
        verbose_name = _("Category Translation")
        verbose_name_plural = _("Category Translations")

    def __str__(self):
        return f"{self.category.name} - {self.get_language_display()}"


class TagTranslation(Translation):
    tag = models.ForeignKey(
        "Tag", on_delete=models.CASCADE, related_name="translations", verbose_name=_("Tag")
    )
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        unique_together = ["tag", "language"]
        verbose_name = _("Tag Translation")
        verbose_name_plural = _("Tag Translations")


class PostTranslation(Translation):
    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE, related_name="translations", verbose_name=_("Post")
    )
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    body = models.TextField(verbose_name=_("Body"))

    class Meta:
        unique_together = ["post", "language"]
        verbose_name = _("Post Translation")
        verbose_name_plural = _("Post Translations")


class Weblog(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="weblogs", verbose_name=_("Owner")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Weblog")
        verbose_name_plural = _("Weblogs")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(TranslatableMixin, models.Model):
    weblog = models.ForeignKey(Weblog, on_delete=models.CASCADE, null=True, verbose_name=_("Weblog"))
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    slug = models.SlugField(verbose_name=_("Slug"))
    image = models.URLField(blank=True, verbose_name=_("Image"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        unique_together = ["weblog", "slug"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.weblog:
            return f"{self.weblog.name} - {self.translated_name}"
        return self.translated_name

    def get_name(self, language_code="en"):
        return self.translate("name", language_code)

    @property
    def translated_name(self):
        language_code = get_language()
        try:
            translation = self.translations.filter(language=language_code).first()
            if translation and translation.name:
                return translation.name
        except Exception:
            pass
        return self.name


class Tag(TranslatableMixin, models.Model):
    weblog = models.ForeignKey(Weblog, on_delete=models.CASCADE, null=True, verbose_name=_("Weblog"))
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    slug = models.SlugField(verbose_name=_("Slug"))
    image = models.URLField(blank=True, verbose_name=_("Image"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        unique_together = ["weblog", "slug"]
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.weblog:
            return f"{self.weblog.name} - {self.translated_name}"
        return self.translated_name

    def get_name(self, language_code="en"):
        return self.translate("name", language_code)

    @property
    def translated_name(self):
        language_code = get_language()
        try:
            translation = self.translations.filter(language=language_code).first()
            if translation and translation.name:
                return translation.name
        except Exception:
            pass
        return self.name


class Post(TranslatableMixin, models.Model):
    weblog = models.ForeignKey(Weblog, on_delete=models.CASCADE, null=True, verbose_name=_("Weblog"))
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    slug = models.SlugField(max_length=100, verbose_name=_("Slug"))
    body = models.TextField(blank=True, verbose_name=_("Body"))
    date = models.DateTimeField(verbose_name=_("Date"))
    post_image = models.ImageField(upload_to=f"{UPLOAD_ROOT}/cover_images", blank=True, verbose_name=_("Post Image"))
    image_url = models.URLField(blank=True, verbose_name=_("Image URL"))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="weblog_posts", verbose_name=_("Author")
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, verbose_name=_("Category"))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_("Tags"))
    is_public = models.BooleanField(default=False, verbose_name=_("Public"))
    views = models.IntegerField(default=0, verbose_name=_("Views"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        unique_together = ["weblog", "slug"]
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.weblog:
            return f"{self.weblog.name} - {self.translated_title}"
        return self.translated_title

    @property
    def translated_title(self):
        language_code = get_language()
        try:
            translation = self.translations.filter(language=language_code).first()
            if translation and translation.title:
                return translation.title
        except Exception:
            pass
        return self.title

    def get_excerpt(self, length=1000):
        if not hasattr(self, "_excerpt"):
            soup = BeautifulSoup(self.body, "html.parser")
            excerpt = ""
            for paragraph in soup.find_all("p"):
                p_content = paragraph.decode_contents()
                p_soup = BeautifulSoup(p_content, "html.parser")

                for img in p_soup.find_all("img"):
                    img.decompose()

                if p_soup.get_text().strip():
                    filtered_p = f"<p>{p_soup.decode_contents()}</p>"
                    excerpt += filtered_p

                if len(excerpt) >= length:
                    break
            self._excerpt = excerpt
        return self._excerpt

    @property
    def excerpt(self):
        return self.get_excerpt()

    def get_processed_body(self):
        if not hasattr(self, "_processed_body"):
            soup = BeautifulSoup(self.body, "html.parser")
            first_p = soup.find("p")

            self._first_paragraph = str(first_p) if first_p else ""
            if first_p:
                first_p.decompose()

            self._processed_body = str(soup)

        return self._processed_body

    @property
    def processed_body(self):
        return self.get_processed_body()

    @property
    def first_paragraph(self):
        if not hasattr(self, "_first_paragraph"):
            self.get_processed_body()
        return self._first_paragraph

    def translate(self, language_code="en", processed_objects=None):
        instance = super().translate(language_code, processed_objects)
        if hasattr(instance, "_processed_body"):
            delattr(instance, "_processed_body")
            delattr(instance, "_first_paragraph")
        return instance


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name=_("Post"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="weblog_comments",
        verbose_name=_("User"),
    )
    anonymous_user = models.ForeignKey(
        "authentication.AnonymousCommentUser",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="weblog_comments",
        verbose_name=_("Anonymous User"),
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies", verbose_name=_("Parent")
    )
    upvotes = models.IntegerField(default=0, verbose_name=_("Upvotes"))
    downvotes = models.IntegerField(default=0, verbose_name=_("Downvotes"))
    body = models.TextField(verbose_name=_("Body"))
    spam_status = models.CharField(
        max_length=10, choices=SPAM_STATUS_CHOICES, default="pending", db_index=True, verbose_name=_("Spam Status")
    )
    spam_checked_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Spam Checked At"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    edited = models.BooleanField(default=False, verbose_name=_("Edited"))
    edited_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Edited At"))
    level = models.IntegerField(default=0, verbose_name=_("Level"))

    @property
    def vote_score(self):
        """Calculate the net vote score (upvotes - downvotes)"""
        return self.upvotes - self.downvotes

    def get_user_vote(self, user):
        """Get the current vote type for a specific user, or None if no vote"""
        if not user.is_authenticated:
            return None
        try:
            vote = self.votes.get(user=user)
            return vote.vote_type
        except CommentVote.DoesNotExist:
            return None

    def toggle_vote(self, user, vote_type):
        """
        Toggle a user's vote on this comment.
        vote_type: 1 for upvote, -1 for downvote
        Returns: (action_taken, new_vote_type)
        action_taken: 'added', 'removed', 'changed'
        new_vote_type: 1, -1, or None
        """
        if not user.is_authenticated:
            return None, None

        try:
            existing_vote = self.votes.get(user=user)
            if existing_vote.vote_type == vote_type:
                # Same vote type - remove the vote
                existing_vote.delete()
                self._update_vote_counts()
                return "removed", None
            else:
                # Different vote type - change the vote
                existing_vote.vote_type = vote_type
                existing_vote.save()
                self._update_vote_counts()
                return "changed", vote_type
        except CommentVote.DoesNotExist:
            # No existing vote - create new vote
            CommentVote.objects.create(comment=self, user=user, vote_type=vote_type)
            self._update_vote_counts()
            return "added", vote_type

    def _update_vote_counts(self):
        """Update the upvotes and downvotes counts based on CommentVote records"""
        upvotes = self.votes.filter(vote_type=1).count()
        downvotes = self.votes.filter(vote_type=-1).count()
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.save(update_fields=["upvotes", "downvotes"])

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["parent", "created_at"]),
        ]
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.post.title} - {self.body[:50]}..."

    def has_user_upvoted(self, user):
        """Check if user has upvoted this comment"""
        return self.get_user_vote(user) == 1

    def has_user_downvoted(self, user):
        """Check if user has downvoted this comment"""
        return self.get_user_vote(user) == -1

    def approve_comment(self):
        """Approve comment and set check timestamp"""
        self.spam_status = "approved"
        self.spam_checked_at = timezone.now()
        self.save(update_fields=["spam_status", "spam_checked_at"])


class CommentVote(models.Model):
    VOTE_CHOICES = [
        (1, _("Upvote")),
        (-1, _("Downvote")),
    ]

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="votes", verbose_name=_("Comment"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="weblog_commentvotes",
        verbose_name=_("User"),
    )
    vote_type = models.IntegerField(choices=VOTE_CHOICES, verbose_name=_("Vote Type"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        unique_together = ["comment", "user"]  # One vote per user per comment
        indexes = [
            models.Index(fields=["comment", "vote_type"]),
        ]
        verbose_name = _("Comment Vote")
        verbose_name_plural = _("Comment Votes")

    def __str__(self):
        vote_str = "upvote" if self.vote_type == 1 else "downvote"
        return f"{self.user.username} {vote_str} on comment {self.comment.id}"
