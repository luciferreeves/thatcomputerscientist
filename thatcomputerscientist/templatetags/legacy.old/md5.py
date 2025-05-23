from django import template

register = template.Library()

@register.filter(name='md5')
def md5(value):
    import hashlib
    return hashlib.md5(str(value).lower().encode('utf-8')).hexdigest() 
