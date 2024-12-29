from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='subdomain')
def subdomain(url, subdomain):
    return url
#     if settings.DEBUG:
#         return url
#     else:
#         url = url.replace(subdomain, '')
#         url = url.replace('//', '/')
#         url = "http://" + subdomain + "." + settings.DOMAIN_NAME + url
#         return url
