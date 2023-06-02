import uuid

from django.conf import settings
from django.core.cache import cache


class UserUUIDMiddleware:
    # assign a uuid to the user if they don't have one
    # store in cookies for 365 days
    def __init__(self, get_response):
        self.get_response = get_response
        self.cookie_name = 'user_uuid'

    def __call__(self, request):
        if not request.COOKIES.get(self.cookie_name):
            response = self.get_response(request)
            response.set_cookie(self.cookie_name, uuid.uuid4(), max_age=31536000)
            return response
        return self.get_response(request)

def userTrackingContextProcessor(request):
    # user tracking context processor - track 3 types of users (anonymous, logged in, admin)
    # based on the user's uuid cookie. Only UUID are necessary to track online users. Then we
    # separate them into anonymous, logged in, and admin users based on their permissions.

    # get the user's uuid from the cookie
    user_uuid = request.COOKIES.get('user_uuid')

    print(user_uuid)

    return {
        'anonymous_users': 0,
        'logged_in_users':0,
        'admin_users': 0,
    }

    # if user_uuid:
    #     # get the user's permissions
    #     is_authenticated = request.user.is_authenticated
    #     is_staff = request.user.is_staff

    #     # refresh online users every 300 seconds, with auto deleting expired keys
    #     cache.set(f"presence_{user_uuid}", {
    #         'is_authenticated': is_authenticated,
    #         'is_staff': is_staff,
    #     }, 300)

    #     # get all online users
    #     online_now = cache.keys('presence_*')

    #     # separate online users into anonymous, logged in, and admin users
    #     anonymous_users = []
    #     logged_in_users = []
    #     admin_users = []

    #     for user in online_now:
    #         user_data = cache.get(user)
    #         if user_data['is_authenticated'] == False and user_data['is_staff'] == False:
    #             anonymous_users.append(user_data)
    #         elif user_data['is_authenticated'] == True and user_data['is_staff'] == False:
    #             logged_in_users.append(user_data)
    #         if user_data['is_staff'] == True:
    #             admin_users.append(user_data)

    #     return {
    #         'anonymous_users': len(anonymous_users),
    #         'logged_in_users': len(logged_in_users),
    #         'admin_users': len(admin_users),
    #     }
