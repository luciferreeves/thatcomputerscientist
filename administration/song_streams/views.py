from django.shortcuts import render


def song_streams(request):
    return render(request, "administration/song_streams.html")
