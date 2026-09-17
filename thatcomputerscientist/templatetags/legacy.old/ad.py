import base64
import os
import random

from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='ad')
def ad(type):
    path = 'static/images/fakeads/{}'.format(type)
    files = os.listdir(path)
    file = random.choice(files)
    # return path
    return "/static/images/fakeads/{}/{}".format(type, file)