from django.utils.deprecation import MiddlewareMixin
from services.users.models import UserProfile
from apps.blog.models import Post


class UserProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                user_profile = UserProfile(user=request.user)
                user_profile.save()
            request.user.profile = user_profile
            request.user.profile.weblogs_created = Post.objects.filter(
                author=request.user
            ).count()
        else:
            request.user.profile = None
