import functools
import requests

from django.conf import settings

from apps.userpage.models import UserProfile


def validate_serializer(serializer):
    def validate(view_method):
        @functools.wraps(view_method)
        def handle(self, request, *args, **kwargs):
            s = serializer(data=request.data)
            if s.is_valid():
                request._request.data = s.data
                return view_method(self, request, *args, **kwargs)
            else:
                return self.invalid_serializer(s)

        return handle

    return validate


def validate_identity(func):
    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            url = settings.USER_CENTER_GATEWAY + '/api/verify'
            headers = {'authorization': token}
            res = requests.get(url=url, headers=headers)
            if res.status_code != 200:
                return self.error('uc server error', 500)
            res_data = res.json()
            if res_data['code'] != 0:
                return self.error('error', 401)
            request._request.uid = res_data['data']
        except:
            return self.error('error', 400)
        return func(self, request, *args, **kwargs)

    return wrapper


def logged_in(func):
    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            url = settings.USER_CENTER_GATEWAY + '/api/verify'
            headers = {'authorization': token}
            res = requests.get(url=url, headers=headers)
            if res.status_code != 200:
                return self.error('uc server error', 500)
            res_data = res.json()
            if res_data['code'] != 0:
                return self.error('error', 401)
            uid = res_data['data']
            me = UserProfile.objects.filter(uid=uid).first()
            if me is None:
                return self.error('error', 400)
            request.me = me
        except:
            return self.error('error', 400)
        return func(self, request, *args, **kwargs)

    return wrapper
