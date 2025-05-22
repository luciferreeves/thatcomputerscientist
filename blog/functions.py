from blog.models import Post


def get_single_post(weblog_slug, post_slug, lang="en"):
    post = (
        Post.objects.select_related("category")
        .filter(weblog__slug=weblog_slug, slug=post_slug, is_public=True)
        .prefetch_related(
            "tags", "translations", "category__translations", "tags__translations"
        )
        .first()
    )
    if post:
        return post.translate(lang)
    return None


def get_all_posts(weblog_slug, lang="en"):
    queryset = (
        Post.objects.filter(weblog__slug=weblog_slug, is_public=True)
        .prefetch_related(
            "tags", "translations", "category__translations", "tags__translations"
        )
        .order_by("-date")
    )

    return Post.translate_queryset(queryset, lang)


def get_recent_posts(lang="en", amount=3, author_username="bobby"):
    queryset = (
        Post.objects.filter(is_public=True, author__username=author_username)
        .prefetch_related(
            "tags", "translations", "category__translations", "tags__translations"
        )
        .order_by("-date")[:amount]
    )

    return Post.translate_queryset(queryset, lang)
