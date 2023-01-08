from .models import Post, Category, Comment
import os
from django.conf import settings
from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.lexers import guess_lexer
from pygments.formatters import HtmlFormatter
import re

def add_excerpt(post):
    soup = BeautifulSoup(post.body, 'html.parser')

    # Create excerpt, count min 1000 characters and max upto next paragraph
    excerpt = ''
    for paragraph in soup.find_all('p'):
        excerpt += str(paragraph)

        if len(excerpt) >= 1000:
            break
    return excerpt

def add_num_comments(post):
    num_comments = Comment.objects.filter(post=post).count()
    return num_comments

def recent_posts():
    recent_posts = Post.objects.filter(is_public=True).order_by('-date')[:5]
    for post in recent_posts:
        post.excerpt = add_excerpt(post)
        post.num_comments = add_num_comments(post)
    return recent_posts

def categories(request):
    categories = Category.objects.all()
    return {'categories': categories}

def archives(request):
    archives = Post.objects.filter(is_public=True).dates('date', 'month', order='DESC')
    return {'archives': archives}

def avatar_list():
    avatar_list = {}
    directory = os.path.join(settings.BASE_DIR, 'static', 'images', 'avatars')
    for directory in os.listdir(directory):
        # ignore hidden files
        if directory.startswith('.'):
            continue
        avatar_list[directory] = os.listdir(os.path.join(settings.BASE_DIR, 'static', 'images', 'avatars', directory))
        # remove hidden files
        for file in avatar_list[directory]:
            if file.startswith('.'):
                avatar_list[directory].remove(file)
    return avatar_list

def highlight_code_blocks(code_block):
    # replace &nbsp; with space
    try:
        cb = code_block.string
    except:
        cb = code_block
    print(cb)
    cb = cb.replace(u'\xa0', u' ')

    # guess the language as there is no data-lang attribute
    try:
        lexer = guess_lexer(cb)
    except:
        lexer = get_lexer_by_name('text')

    # highlight the code
    formatter = HtmlFormatter(noclasses=True, style='native')
    highlighted_code = highlight(cb, lexer, formatter)

    return highlighted_code

def comment_processor(comment):
    # escape html tags
    comment = re.sub(r'<', '&lt;', comment)
    comment = re.sub(r'>', '&gt;', comment)

    # any text between ``` and ``` must be highlighted as code
    code_blocks = re.findall(r'```(.+?)```', comment, re.DOTALL)
    for code_block in code_blocks:
        comment = comment.replace('```' + code_block + '```', highlight_code_blocks(code_block))

    # retain line breaks, for every newline character, add a <br> tag
    comment = comment.replace('\n', '<br>')

    # replace multiple <br> tags with a single <br> tag
    comment = re.sub(r'<br>(\s*<br>)+', '<br><br>', comment)

    comment = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', comment)
    comment = re.sub(r'__(.+?)__', r'<i>\1</i>', comment)
    comment = re.sub(r'~~(.+?)~~', r'<s>\1</s>', comment)

    return comment

