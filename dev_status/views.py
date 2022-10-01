from django.shortcuts import render
from github import Github
from dotenv import load_dotenv
import os

load_dotenv()

# Create your views here.

def home(request):
    g = Github(os.getenv('GH_TOKEN'))
    repo = g.get_repo('luciferreeves/thatcomputerscientist')
    contents = repo.get_contents('')
    files = []
    while contents:
        file_content = contents.pop(0)
        files.append(file_content)
    context = {
        'title': 'Source Code',
        'files': files,
    }
    return render(request, 'dev_status/home.html', context)

def tree(request, path=None):
    g = Github(os.getenv('GH_TOKEN'))
    repo = g.get_repo('luciferreeves/thatcomputerscientist')
    path = '' if not path else path
    parent = '' if len(path.split('/')) == 1 else '/'.join(path.split('/')[:-1])
    contents = repo.get_contents(path)
    files = []
    while contents:
        file_content = contents.pop(0)
        files.append(file_content)
    context = {
        'title': 'Tree - {}'.format(path),
        'files': files,
        'parent': parent,
    }
    return render(request, 'dev_status/home.html', context)

def raw(request, path):
    g = Github(os.getenv('GH_TOKEN'))
    repo = g.get_repo('luciferreeves/thatcomputerscientist')
    path = '' if not path else path
    parent = '' if len(path.split('/')) == 1 else '/'.join(path.split('/')[:-1])
    contents = repo.get_contents(path)
    context = {
        'title': 'File - {}'.format(path),
        'file': contents.html_url,
        'parent': parent,
    }
    return render(request, 'dev_status/home.html', context)