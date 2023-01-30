import random
from django import template

register = template.Library()

@register.simple_tag()
def random_numbers(a, b=None):
    if b is None:
        a, b = 0, a
    return random.randint(a, b)
