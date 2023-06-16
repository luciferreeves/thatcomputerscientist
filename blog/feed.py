from django.contrib.syndication.views import Feed
from django.utils import feedgenerator
from django.utils.feedgenerator import Enclosure
import requests
from .context_processors import add_excerpt
from .models import Post
from django.conf import settings

request_domain = settings.DEBUG and 'https://preview.thatcomputerscientist.com' or 'https://thatcomputerscientist.com'

class RSSFeed(Feed):
    title = 'That Computer Scientist - RSS Feed'
    link = '/weblog/'
    description = 'RSS Feed for That Computer Scientist Weblog'
    feed_type = feedgenerator.Rss201rev2Feed

    def items(self):
        unique_items = set()
        items = []

        for post in Post.objects.filter(is_public=True).order_by('-date'):
            if post.id not in unique_items:
                unique_items.add(post.id)
                items.append(post)

        return items
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        post_excerpt = add_excerpt(item)
        return post_excerpt
    
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
