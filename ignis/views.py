from django.shortcuts import render
from PIL import Image
from io import BytesIO
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import base64
from blog.models import Post

# Create your views here.
@csrf_exempt
def tex(request):
    # get expression from request query
    expression = request.GET.get('expr').replace('"', '').strip()
    if not expression:
        return HttpResponse('No expression provided!', status=400)

    import requests

    image = requests.get('https://latex.codecogs.com/png.image?%5Cinline%20%5Clarge%20%5Cdpi%7B300%7D%5Cbg%7Btransparent%7D' + expression).content

    # Image is a transparent GIF with black text. Invert the colors.
    image = Image.open(BytesIO(image))
    image = image.convert('RGBA')
    image = Image.eval(image, lambda x: 255 - x)

    # Convert back to gif and return
    output = BytesIO()
    image.save(output, format='GIF')
    return HttpResponse(output.getvalue(), content_type='image/gif')

@csrf_exempt
def post_image(request, post_id):
    pi = Post.objects.get(id=post_id).post_image
    if not pi:
        return HttpResponse('No image found!', status=404)
    
    # convert base64 data src to image
    image = base64.b64decode(pi.split(',')[1])
    return HttpResponse(image, content_type='image/png')
