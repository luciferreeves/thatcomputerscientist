import os
from django.conf import settings
import random
from django import template
import base64

register = template.Library()

@register.filter(name='ad')
def ad(type):
    path = 'static/images/fakeads/{}'.format(type)
    files = os.listdir(path)
    file = random.choice(files)
    # return path
    return "/static/images/fakeads/{}/{}".format(type, file)