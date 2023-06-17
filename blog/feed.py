import re

import requests
# from .context_processors import add_excerpt
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.utils import feedgenerator
from django.utils.feedgenerator import Enclosure

from .models import Post

request_domain = settings.DEBUG and 'https://preview.thatcomputerscientist.com' or 'https://thatcomputerscientist.com'
mathjax_path = f'{request_domain}/static/js/MathJax/MathJax.js?config=default'
mathjax_config = '''
<script type="text/x-mathjax-config">
    MathJax.Hub.Config({
        jax: ["input/TeX", "output/HTML-CSS"],
        tex2jax: {
            inlineMath: [['$','$'], ['\\(','\\)']],
            processEscapes: true
        },
        "HTML-CSS": { availableFonts: ["TeX"] },
    });
</script>
'''

class RSSFeed(Feed):
    title = 'That Computer Scientist'
    link = '/weblog/'
    description = 'RSS Feed for That Computer Scientist Weblog'
    feed_type = feedgenerator.Rss201rev2Feed

    def items(self):
        return Post.objects.all().order_by('-date')
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        r = requests.get(f'{request_domain}/weblog/{item.slug}')
        soup = BeautifulSoup(r.text, 'html.parser')
        article_body = soup.find(id='article-body')
        for img in article_body.find_all('img'):
            if not img.get('id'):
                img['style'] = 'float: left; margin: 5px 11px 5px 0px; max-width: 710px;' + img.get('style', '')

        article_body = str(article_body)
        article_body = re.sub(r"[\x00-\x08\x0B-\x1F\x7F-\x9F]", "", str(article_body))
        article_body += f'<script type="text/javascript" src="{mathjax_path}"></script>'
        article_body += mathjax_config
        return article_body

    def item_link(self, item):
        return f'{request_domain}/weblog/{item.slug}'
    
    def item_pubdate(self, item):
        return item.date

    def get_cl(self, url):
        r = requests.head(url)
        return str(r.headers['Content-Length'])

    def item_enclosures(self, item):
        return [
            Enclosure(
                url=f'{request_domain}/ignis/post_image/1200/{item.id}.gif',
                length=self.get_cl(f'{request_domain}/ignis/post_image/1200/{item.id}.gif'),
                mime_type='image/gif',
            )
        ]
