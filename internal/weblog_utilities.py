from apps.blog.models import Post, Comment
from bs4 import BeautifulSoup


def add_excerpt(post, lang="en"):
    if lang == "ja":
        soup = BeautifulSoup(post.body_ja, "html.parser")
    else:
        soup = BeautifulSoup(post.body, "html.parser")
    excerpt = ""
    for paragraph in soup.find_all("p"):
        paragraph = "<p>" + str(paragraph.text) + "</p>"
        excerpt += str(paragraph)

        if len(excerpt) >= 1000:
            break
    print(excerpt)
    return excerpt


def add_num_comments(post):
    num_comments = Comment.objects.filter(post=post).count()
    return num_comments


def recent_weblogs(lang="en"):
    recent_posts = Post.objects.filter(is_public=True).order_by("-date")[:5]
    for post in recent_posts:
        post.excerpt = add_excerpt(post, lang)
        post.num_comments = add_num_comments(post)
    return recent_posts
