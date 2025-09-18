from django.shortcuts import render


def journals(request):
    return render(request, "journals/journals.html")
