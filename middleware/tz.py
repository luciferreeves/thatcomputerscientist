import requests


# make sure you add `TimezoneMiddleware` appropriately in settings.py
class TimezoneMiddleware(object):
    """
    Middleware to properly handle the users timezone
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # get the user's timezone from the cookie
        user_timezone = request.COOKIES.get('user_timezone')

        if not user_timezone:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            
            if x_forwarded_for:
                remote_ip = x_forwarded_for.split(',')[0]
            else:
                remote_ip = request.META.get('REMOTE_ADDR')
        
            geo_data = requests.get(f'http://ip-api.com/json/{remote_ip}').json()
            user_timezone = geo_data['timezone']

            if user_timezone:
                response = self.get_response(request)
                response.set_cookie('user_timezone', user_timezone, max_age=31536000)
                return response
            return self.get_response(request)
