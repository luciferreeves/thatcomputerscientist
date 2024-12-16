from django.utils.deprecation import MiddlewareMixin
from services.users.models import UserProfile


class UserProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user=request.user)
            request.user.profile = user_profile
        else:
            request.user.profile = None
