from blog.models import Post, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count


def get_posts(
    weblog_slug,
    lang="en",
    query="",
    sort="date",
    order="asc",
    category_slug="all",
    page=1,
    per_page=10,
):
    queryset = (
        Post.objects.filter(weblog__slug=weblog_slug, is_public=True)
        .select_related("weblog", "category", "author")
        .prefetch_related(
            "tags", "translations", "category__translations", "tags__translations"
        )
    )

    if query:
        queryset = queryset.filter(Q(title__icontains=query) | Q(body__icontains=query))

    if category_slug != "all":
        queryset = queryset.filter(category__slug=category_slug)

    sort_mapping = {
        "date": "date",
        "title": "title",
        "views": "views",
        "comments": "comment_count",
    }

    if sort == "comments":
        queryset = queryset.annotate(comment_count=Count("comments"))

    sort_field = sort_mapping.get(sort, "date")

    if order == "desc":
        sort_field = f"-{sort_field}"

    queryset = queryset.order_by(sort_field)
    translated_queryset = Post.translate_queryset(queryset, lang)

    paginator = Paginator(translated_queryset, per_page)

    try:
        paginated_posts = paginator.page(page)
    except PageNotAnInteger:
        paginated_posts = paginator.page(1)
        page = 1
    except EmptyPage:
        paginated_posts = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    return {
        "posts": paginated_posts.object_list,
        "paginator": paginator,
        "page_objects": paginated_posts,
        "page": page,
        "per_page": per_page,
        "total_pages": paginator.num_pages,
        "has_previous": paginated_posts.has_previous(),
        "has_next": paginated_posts.has_next(),
        "previous_page_number": (
            paginated_posts.previous_page_number()
            if paginated_posts.has_previous()
            else None
        ),
        "next_page_number": (
            paginated_posts.next_page_number() if paginated_posts.has_next() else None
        ),
        "total_posts": paginator.count,
    }


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


# def get_all_posts(weblog_slug, lang="en"):
#     queryset = (
#         Post.objects.filter(weblog__slug=weblog_slug, is_public=True)
#         .prefetch_related(
#             "tags", "translations", "category__translations", "tags__translations"
#         )
#         .order_by("-date")
#     )

#     return Post.translate_queryset(queryset, lang)


def get_all_categories(weblog_slug, lang="en"):
    queryset = (
        Category.objects.filter(weblog__slug=weblog_slug)
        .prefetch_related("translations")
        .order_by("name")
    )

    return Category.translate_queryset(queryset, lang)


def get_recent_posts(lang="en", amount=3, author_username="bobby"):
    queryset = (
        Post.objects.filter(is_public=True, author__username=author_username)
        .prefetch_related(
            "tags", "translations", "category__translations", "tags__translations"
        )
        .order_by("-date")[:amount]
    )

    return Post.translate_queryset(queryset, lang)
