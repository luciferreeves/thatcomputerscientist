from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.shortcuts import render

from users.models import UserProfile


# Create your views here.
def home(request):
    subdomain = request.subdomain
    try:
        user = User.objects.get(username=subdomain)
        try:
            user_profile = UserProfile.objects.get(user=user)
            is_public = user_profile.is_public
            if is_public:
                return render(request, 'userpages/home.html', {'title': 'Homepage', 'username': str(user.username).capitalize()})
            else:
                raise Http404('{} is not public.'.format(subdomain))
        except UserProfile.DoesNotExist:
            raise Http404('{} has no profile.'.format(subdomain))
        
    except User.DoesNotExist:
        raise Http404('{} does not exist.'.format(subdomain))

