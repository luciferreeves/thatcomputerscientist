import re

import requests
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.utils import feedgenerator
from django.utils.feedgenerator import Enclosure

from .models import Post

request_domain = settings.DEBUG and 'https://preview.thatcomputerscientist.com' or 'https://thatcomputerscientist.com'

class RSSFeed(Feed):
    title = 'That Computer Scientist'
    link = '/weblog/'
    description = 'RSS Feed for That Computer Scientist Weblog'
    feed_type = feedgenerator.Rss201rev2Feed

    def items(self):
        return Post.objects.all().filter(is_public=True).order_by('-date')[:10]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        body = re.sub(r"[\x00-\x08\x0B-\x1F\x7F-\x9F]", "", str(item.body))
        return body

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
