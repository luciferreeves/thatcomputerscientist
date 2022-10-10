from django.template import Library
from django.urls import reverse
from django.conf import settings

register = Library()

@register.simple_tag
def subdomain_url(view_name, subdomain = None, referrer = None, *args, **kwargs):
    if subdomain == 'www':
        subdomain = None

    if subdomain is None:
        return reverse(view_name, args=args, kwargs=kwargs)

    if referrer:
        return '{}://{}{}{}?referrer={}'.format(
        'https' if settings.SECURE_SSL_REDIRECT else 'http',
        subdomain,
        settings.HOSTS[0],
        reverse(view_name, args=args, kwargs=kwargs),
        referrer
    )

    return '{}://{}{}{}'.format(
        'https' if settings.SECURE_SSL_REDIRECT else 'http',
        subdomain,
        settings.HOSTS[0],
        reverse(view_name, args=args, kwargs=kwargs)
    )
