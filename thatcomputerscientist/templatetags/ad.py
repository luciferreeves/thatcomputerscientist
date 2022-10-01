import os
from django.conf import settings
import random
from django import template
import base64

register = template.Library()

@register.filter(name='ad')
def ad(type):
    path = 'static/images/ads/{}'.format(type)
    files = os.listdir(path)
    file = random.choice(files)
    with open('{}/{}'.format(path, file), 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
        ext = file.split('.')[-1]
        return 'data:image/{};base64,{}'.format(ext, data)