from blog.models import Post, Category, Tag, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, F, Prefetch
from internal.weblog_utilities import highlight_code, get_post_color


def get_posts(
    weblog_slug,
    lang="en",
    query="",
    sort="date",
    order="asc",
    category_slug="all",
    tag_slug="all",
    year=None,
    month=None,
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

    if tag_slug != "all":
        queryset = queryset.filter(tags__slug=tag_slug)

    if year and month:
        queryset = queryset.filter(date__year=year, date__month=month)
    elif year:
        queryset = queryset.filter(date__year=year)
    elif month:
        queryset = queryset.filter(date__month=month)

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

    for post in paginated_posts:
        post.color = get_post_color(post)

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


def get_single_post(weblog_slug, post_slug, lang="en", comment_sort="best"):
    if comment_sort == "best":
        comments_order = ["-score", "-created_at"]
        comments_annotation = {"score": F("upvotes") - F("downvotes")}
    elif comment_sort == "newest":
        comments_order = ["-created_at"]
        comments_annotation = {}
    elif comment_sort == "oldest":
        comments_order = ["created_at"]
        comments_annotation = {}
    else:
        comments_order = ["-score", "-created_at"]
        comments_annotation = {"score": F("upvotes") - F("downvotes")}

    prefetch_comments = Prefetch(
        "comments",
        queryset=(
            Comment.objects.select_related("user", "anonymous_user")
            .annotate(**comments_annotation)
            .order_by(*comments_order)
            if comments_annotation
            else Comment.objects.select_related("user", "anonymous_user").order_by(
                *comments_order
            )
        ),
    )

    post = (
        Post.objects.select_related("category")
        .filter(weblog__slug=weblog_slug, slug=post_slug, is_public=True)
        .prefetch_related(
            "tags",
            "translations",
            "category__translations",
            "tags__translations",
            prefetch_comments,
        )
        .first()
    )
    if post:
        post.color = get_post_color(post)
        post = post.translate(lang)
        post.body = highlight_code(post.body)
        return post
    return None


def get_categories(weblog_slug, lang="en"):
    queryset = (
        Category.objects.filter(weblog__slug=weblog_slug)
        .prefetch_related("translations")
        .annotate(post_count=Count("post", filter=Q(post__is_public=True)))
        .order_by("name")
    )

    return Category.translate_queryset(queryset, lang)


def get_tags(weblog_slug, lang="en"):
    queryset = (
        Tag.objects.filter(weblog__slug=weblog_slug)
        .prefetch_related("translations")
        .annotate(post_count=Count("post", filter=Q(post__is_public=True)))
        .order_by("name")
    )

    return Tag.translate_queryset(queryset, lang)


def get_archives(weblog_slug):
    from django.db.models import Count

    queryset = Post.objects.filter(weblog__slug=weblog_slug, is_public=True).dates(
        "date", "month", order="DESC"
    )

    archives = []
    for date in queryset:
        post_count = Post.objects.filter(
            weblog__slug=weblog_slug,
            is_public=True,
            date__year=date.year,
            date__month=date.month,
        ).count()

        archives.append(
            {
                "pretty": date.strftime("%B %Y"),
                "date": date,
                "month": date.strftime("%m"),
                "year": date.strftime("%Y"),
                "post_count": post_count,
            }
        )
    return archives


def handle_comment_vote(comment_id, user, vote_type):
    try:
        comment = Comment.objects.get(id=comment_id)
        comment.toggle_vote(user, vote_type)
        return True, None
    except Comment.DoesNotExist:
        return False, "Comment not found."
