from multiprocessing import context
from django.shortcuts import render
from github import Github
from dotenv import load_dotenv
import os

load_dotenv()

# Create your views here.

def home(request, r='thatcomputerscientist', p=None):
    g = Github(os.getenv('GH_TOKEN'))
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
        return render(request, 'dev_status/home.html', context)