from django import template

register = template.Library()

@register.filter(name='replace')
# Takes two arguments: the string to be replaced and the string to replace it with
def replace(value, arg):
    return value.replace(arg, '')
