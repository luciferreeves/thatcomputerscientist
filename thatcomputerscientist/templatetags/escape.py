from django import template
import re

register = template.Library()

@register.filter(name='escape')
def escape(value):
    val = value.replace("\\", '\\\\')
    val = re.sub(r'`', r'\`', val) 
    return val
