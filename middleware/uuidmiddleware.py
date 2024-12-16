# import json
# import uuid

# import redis
# import os
# from dotenv import load_dotenv

# load_dotenv()

# redis_instance = redis.StrictRedis(
#   host=os.getenv('REDIS_HOST'),
#   port=os.getenv('REDIS_PORT'),
#   password=os.getenv('REDIS_PASSWORD'),
#   db=0
# )

# class UserUUIDMiddleware:
#     # assign a uuid to the user if they don't have one
#     # store in cookies for 365 days
#     def __init__(self, get_response):
#         self.get_response = get_response
#         self.cookie_name = 'user_uuid'

#     def __call__(self, request):
#         if not request.COOKIES.get(self.cookie_name):
#             response = self.get_response(request)
#             response.set_cookie(self.cookie_name, uuid.uuid4(), max_age=31536000)
#             return response
#         return self.get_response(request)

# def userTrackingContextProcessor(request):
#     # ignore /rss/ path
#     if '/rss/' in request.path:
#         return {
#             'anonymous_users': 0,
#             'logged_in_users': 0,
#             'admin_users': 0,
#         }

#     # user tracking context processor - track 3 types of users (anonymous, logged in, admin)
#     # based on the user's uuid cookie. Only UUID are necessary to track online users. Then we
#     # separate them into anonymous, logged in, and admin users based on their permissions.

#     # get the user's uuid from the cookie
#     user_uuid = request.COOKIES.get('user_uuid')
#     user_data = {
#         'is_authenticated': request.user.is_authenticated,
#         'is_staff': request.user.is_staff,
#     }

#     redis_instance.set(f"presence_{user_uuid}", json.dumps(user_data), ex=300)

#     # get all online users
#     online_now = redis_instance.keys('presence_*')

#     # separate online users into anonymous, logged in, and admin users
#     anonymous_users = []
#     logged_in_users = []
#     admin_users = []

#     for user in online_now:
#         user_data = redis_instance.get(user)
#         user_data = json.loads(user_data)
#         if user_data['is_authenticated'] == False and user_data['is_staff'] == False:
#             anonymous_users.append(user_data)
#         elif user_data['is_authenticated'] == True and user_data['is_staff'] == False:
#             logged_in_users.append(user_data)
#         if user_data['is_staff'] == True:
#             admin_users.append(user_data)

#     an = len(anonymous_users)
#     lo = len(logged_in_users)
#     ad = len(admin_users)
#     if user_uuid is not None:
#         an = max((an - 1), 0) if lo + ad > 0 else max(an - 1, 1)

#     return {
#         'anonymous_users': an,
#         'logged_in_users': lo,
#         'admin_users': ad,
#     }
