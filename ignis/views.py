from PIL import Image
from io import BytesIO
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import base64
from blog.models import Post
from .objectstorage import ObjectStorage
import base64
import _md5
import json
from .github import get_cover

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

@csrf_exempt
def get_image(request, slug, md5):
    object_storage = ObjectStorage()
    image = object_storage.get_object(slug, md5)
    return HttpResponse(base64.b64decode(image.data), content_type=image.metadata)

@csrf_exempt
def cover_image(request, repository):
    url = 'https://socialify.git.ci/luciferreeves/{}/image?font=KoHo&language=1&name=1&pattern=Floating%20Cogs&theme=Dark'.format(repository)
    cover_store = ObjectStorage()
    image_hash = _md5.md5(url.encode()).hexdigest()
    if not cover_store.object_exists('github_covers', image_hash):
        image = get_cover(url)
        data = base64.b64encode(image).decode('utf-8')
        cover_store.create_object(md5=image_hash, metadata='image/png', data=data, name='github_covers')
    return HttpResponse(base64.b64decode(cover_store.get_object('github_covers', image_hash).data), content_type='image/png')
        # cover_store.create_object(md5=image_hash, metadata='image/png', data=data, name='github_covers'))

def upload_image(request):
    if request.method == 'POST':
        if not request.user.is_authenticated and not request.user.is_staff:
            return HttpResponse('Unauthorized', status=401)
        if not request.FILES.get('image'):
            return HttpResponse('No image provided!', status=400)
        if not request.POST.get('slug'):
            return HttpResponse('No slug provided!', status=400)
        
        # upload image to object storage
        image = request.FILES['image']
        slug = request.POST.get('slug')
        object_storage = ObjectStorage()
        object_storage.create_directory(slug)
        

        image_data = image.read()
        metadata = image.content_type

        image_hash = _md5.md5(image_data).hexdigest()
        data = base64.b64encode(image_data).decode('utf-8')

        if not object_storage.object_exists(slug, image_hash):
            object_storage.create_object(md5=image_hash, metadata=metadata, data=data, name=slug)

        # return json response
        response = {
            'url': "/ignis/image/{}/{}".format(slug, image_hash)
        }
        
        return HttpResponse(json.dumps(response), content_type='application/json', status=200)


def mvdir(request):
    if not request.user.is_authenticated and not request.user.is_staff:
        return HttpResponse('Unauthorized', status=401)
    object_storage = ObjectStorage()
    
    # get from query params
    old_name = request.GET.get('old')
    new_name = request.GET.get('new')

    if not old_name or not new_name:
        return HttpResponse('No name provided!', status=400)

    if old_name == "":
        object_storage.create_directory(new_name)
        return HttpResponse(json.dumps({'status': 'success'}), content_type='application/json', status=200)
    else:
        object_storage.rename_directory(old_name, new_name)
        return HttpResponse(json.dumps({'status': 'success'}), content_type='application/json', status=200)
