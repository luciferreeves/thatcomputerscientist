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
    repos = []
    user = g.get_user()
    for repo in user.get_repos(type=filter, sort=sort, direction=direction):
        if 'luciferreeves' in repo.full_name:
            if search != '':
                search = search.lower()
                search = ''.join(e for e in search if e.isalnum())
                repo_name = repo.name.lower()
                repo_name = ''.join(e for e in repo_name if e.isalnum())
                repo_desc = repo.description.lower() if repo.description else ''
                repo_desc = ''.join(e for e in repo_desc if e.isalnum())
                if search in repo_name or search in repo_desc:
                    repos.append(repo)
            else:
                repos.append(repo)

    context['repo_length'] = len(repos)

    # Pagination
    start = (int(page) - 1) * int(items)
    end = start + int(items)
    repos = repos[start:end]

    context['title'] = '{} Repositories'.format(str(filter).capitalize())
    context['repos'] = repos
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