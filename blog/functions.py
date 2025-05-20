from blog.models import Post


def get_recent_posts(lang="en", amount=3, author_username="bobby"):
    queryset = (
        Post.objects.filter(is_public=True, author__username=author_username)
        .prefetch_related(
            "tags", "translations", "category__translations", "tags__translations"
        )
        .order_by("-date")[:amount]
    )

    return Post.translate_queryset(queryset, lang)
