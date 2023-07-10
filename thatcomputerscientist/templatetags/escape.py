from django import template

register = template.Library()

@register.filter(name='escape')
def escape(value):
    return value.replace("`", "\`")
