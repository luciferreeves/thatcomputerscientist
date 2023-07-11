from django.shortcuts import render

# Create your views here.
TEMPLATE_BASE_PATH = '@solitude'

def home(request):
    return render(request, f'{TEMPLATE_BASE_PATH}/welcome.html')
