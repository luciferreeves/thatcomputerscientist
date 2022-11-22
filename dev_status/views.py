from django.shortcuts import render
from github import Github
from dotenv import load_dotenv
import os
import math

load_dotenv()
g = Github(os.getenv('GH_TOKEN'))

# Create your views here.
def home(request):
    page = request.GET.get('page') or 1
    items = request.GET.get('items') or 10
    filter = request.GET.get('filter') or 'all'
    sort = request.GET.get('sort') or 'updated'
    direction = request.GET.get('direction') or 'desc'
    search = request.GET.get('search') or ''
    if not request.user.is_authenticated:
        filter = 'public'
    context = {}
    repos = g.get_user().get_repos(type=filter, sort=sort, direction=direction)

    if search != '':
        search = search.lower()
        repos = [repo for repo in repos if search in str(repo.name).lower() or search in str(repo.description).lower()]
    repos = [repo for repo in repos if 'luciferreeves' in str(repo.full_name).lower()]

    context['repo_length'] = len(repos)
    context['repos'] = repos[(int(page) - 1) * int(items):int(page) * int(items)]
    context['title'] = '{} Repositories'.format(str(filter).capitalize())
    context['page'] = int(page)
    context['items'] = int(items)
    context['num_pages'] = math.ceil(context['repo_length'] / int(items))
    context['filter'] = filter
    context['sort'] = sort
    context['direction'] = direction
    context['search'] = search
    print(context)

    return render(request, 'dev_status/home.html', context)

def get_repo(request, r='thatcomputerscientist', p=None):
    repository = 'luciferreeves/{}'.format(r)
    parent = None
    if p and not len(p.split('/')) == 0:
        parent = '/'.join(p.split('/')[:-1])
    contents = g.get_repo(repository).get_contents(p or '')
    context = {}
    try:
        files = []
        while contents:
            file_content = contents.pop(0)
            files.append(file_content)
        context['title'] = 'Tree - {}'.format(p)
        context['files'] = files
        context['parent'] = parent
        context['repo'] = r
    except:
        context['title'] = 'File - {}'.format(p)
        context['file'] = contents.html_url
        context['parent'] = parent
        context['repo'] = r
    finally:
        return render(request, 'dev_status/repo.html', context)