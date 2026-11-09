import re

from django import template

register = template.Library()

@register.filter(name='remove_tags')
# Takes a string and removes all HTML tags from it
def remove_tags(value):
    # replace anything that matches '<tag>' or '</tag>' with ''
    pattern = r'(<([^>]+)>)'
    # replace globally and ignore case
    return re.sub(pattern, '', value, flags=re.IGNORECASE)