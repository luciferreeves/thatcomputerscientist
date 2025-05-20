from django.utils.deprecation import MiddlewareMixin
from users.models import UserProfile

class UserProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                user_profile = UserProfile(user=request.user)
                user_profile.save()
            request.user.profile = user_profile
        else:
            request.user.profile = None