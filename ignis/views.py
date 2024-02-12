import json
from io import BytesIO
import os
import requests
from captcha.image import ImageCaptcha
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from PIL import Image

from blog.models import Post
from users.tokens import CaptchaTokenGenerator

from .models import PostImage, RepositoryTitle

# from .github import get_cover

# Create your views here.
@csrf_exempt
def tex(request):
    # get expression from request query
    expression = request.GET.get('expr').replace('"', '').strip()
    if not expression:
        return HttpResponse('No expression provided!', status=400)

    import requests

    image = requests.get('https://latex.codecogs.com/png.image?%5Cinline%20%5Clarge%20%5Cdpi%7B200%7D%5Cbg%7Btransparent%7D' + expression).content

    # Image is a transparent GIF with black text. Invert the colors.
    image = Image.open(BytesIO(image))
    image = image.convert('RGBA')
    image = Image.eval(image, lambda x: 255 - x)

    # Convert back to gif and return
    output = BytesIO()
    image.save(output, format='GIF')
    return HttpResponse(output.getvalue(), content_type='image/gif')

@csrf_exempt
def post_image(request, size, post_id):
    post_id = post_id.replace('.gif', '')
    pi = Post.objects.get(id=post_id)
    if not pi:
        return HttpResponse('No image found!', status=404)
    
    # open image and return
    image = pi.post_image
    with open(image.path, 'rb') as f:
        # resize image
        size = int(size)
        if size != 0:

            # set min and max size
            if size < 100:
                size = 100
            elif size > 1000:
                size = 1000
            
            image = Image.open(f)
            # resize width to size, compute height
            width, height = image.size
            height = int(height * (size / width))
            width = size

            # resize image
            image = image.resize((width, height), Image.ANTIALIAS)
            output = BytesIO()
            image.save(output, format='GIF')
            return HttpResponse(output.getvalue(), content_type='image/gif')
        else:
            return HttpResponse(f.read(), content_type='image/gif')

@csrf_exempt
def get_image(request, post_id, image_name):
    # get image from post_id
    pi = PostImage.objects.filter(post=Post.objects.get(id=post_id), name=image_name)
    if not pi:
        return HttpResponse('No image found!', status=404)
    
    # open image and return
    image = pi[0].image
    with open(image.path, 'rb') as f:
        image_file = f.read()
        # convert to gif
        image = Image.open(BytesIO(image_file))
        # check image format
        if image.format != 'GIF':
            image = image.convert('RGBA')
            output = BytesIO()
            image.save(output, format='GIF')
            image_file = output.getvalue()
        return HttpResponse(image_file, content_type='image/gif')

@csrf_exempt
def cover_image(request, repository):
    force_reload = request.GET.get('force_reload')
    repository = repository.replace('.gif', '')
    # check if the image is in RepositoryTitles
    try:
        if force_reload:
            raise Exception('Force reload')
        repository_title = RepositoryTitle.objects.get(repository=repository)
        image = repository_title.image
    except:
        # image is not in RepositoryTitles
        # get image
        url = 'https://socialify.thatcomputerscientist.com/luciferreeves/{}/png?font=KoHo&language=1&language2=1&name=1&theme=Dark&pattern=Solid'.format(repository)
        image = requests.get(url).content

        # reduce image size to 320x160
        image = Image.open(BytesIO(image))
        image = image.resize((320, 160), Image.ANTIALIAS)

        # remove black background
        image = image.convert('RGBA').getdata()
        new_data = []
        for item in image:
            if item[0] == 0 and item[1] == 0 and item[2] == 0:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)

        # Convert back to png and return
        output = BytesIO()
        image = Image.new('RGBA', (320, 160))
        image.putdata(new_data)
        image.save(output, format='GIF')
        image = output.getvalue()

        # save image to RepositoryTitles
        image = ContentFile(image, name='{}.png'.format(repository))
        repository_title = RepositoryTitle(repository=repository, image=image)
        repository_title.save()

    return HttpResponse(image, content_type='image/gif')


def upload_image(request):
    if request.method == 'POST':
        if not request.user.is_authenticated and not request.user.is_staff:
            return HttpResponse('Unauthorized', status=401)
        if not request.FILES.get('image'):
            return HttpResponse('No image provided!', status=400)
        if not request.POST.get('id'):
            return HttpResponse('No id provided!', status=400)
        
        # upload image to PostImage model
        image = request.FILES['image']
        post_id = request.POST['id']
        # check if image already exists
        pi = PostImage.objects.filter(post=Post.objects.get(id=post_id), name=image.name)
        if pi:
            # image already exists, delete it
            pi[0].delete()
        # save image to post_id
        pi = PostImage(image=image, post=Post.objects.get(id=post_id), name=image.name)
        pi.save()
        response = {
            'url': '/ignis/image/{}/{}'.format(post_id, pi.name)
        }
        return HttpResponse(json.dumps(response), content_type='application/json')
    return HttpResponse('Method not allowed', status=405)

def captcha_image(request, captcha_string):
    captcha = CaptchaTokenGenerator().decrypt(captcha_string)
    imgcaptcha = ImageCaptcha()
    data = imgcaptcha.generate(captcha)
    return HttpResponse(data, content_type='image/png')

def socialify(request):
    repo = request.GET.get('repo')
    theme = request.GET.get('theme')
    font = request.GET.get('font')
    pattern = request.GET.get('pattern')
    name = request.GET.get('name')
    description = request.GET.get('description')
    language_1 = request.GET.get('language_1')
    language_2 = request.GET.get('language_2')
    stargazers = request.GET.get('stargazers')
    forks = request.GET.get('forks')
    issues = request.GET.get('issues')
    pulls = request.GET.get('pulls')

    url = 'https://socialify.thatcomputerscientist.com/{}/png?description={}&font={}&forks={}&issues={}&language={}&language2={}&name={}&owner=1&pattern={}&pulls={}&stargazers={}&theme={}'.format(repo, description, font, forks, issues, language_1, language_2, name, pattern, pulls, stargazers, theme)

    image_unique_name = url.replace('https://socialify.thatcomputerscientist.com/', '').replace('/', '_')
    image_path = 'images/repo_socialify_cache'
    image_path = '{}/{}.png'.format(image_path, image_unique_name)

    if repo.split('/')[0] == 'luciferreeves':
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                image = f.read()
                return HttpResponse(image, content_type='image/png')

    req = requests.get(url)
    image = req.content
    status = req.status_code

    if status == 200:
        if not os.path.exists('images/repo_socialify_cache'):
            os.makedirs('images/repo_socialify_cache')

        with open(image_path, 'wb') as f:
            if repo.split('/')[0] == 'luciferreeves':
                f.write(image)

        return HttpResponse(image, content_type='image/png')
    else:
        with open('static/images/site/utgi.gif', 'rb') as f:
            image = f.read()
            return HttpResponse(image, content_type='image/gif')

