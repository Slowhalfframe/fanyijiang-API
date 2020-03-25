from rest_framework.views import APIView
from django.conf import settings
from django.http.response import JsonResponse
import requests

from apps.userpage.models import UserProfile


class CustomAPIView(APIView):

    def response(self, data):
        return JsonResponse(data)

    def success(self, data=None, code=0):
        return self.response({"code": code, "data": data})

    def error(self, error, code):
        return self.response({"code": code, "error": error})

    def extract_errors(self, errors, key="field"):
        if isinstance(errors, dict):
            if not errors:
                return key, "Invalid field"
            key = list(errors.keys())[0]
            return self.extract_errors(errors.pop(key), key)
        elif isinstance(errors, list):
            return self.extract_errors(errors[0], key)

        return key, errors

    def invalid_serializer(self, serializer):
        key, error = self.extract_errors(serializer.errors)
        if key == "non_field_errors":
            error = error
        else:
            error = "{0}: {1}".format(key, error)
        return self.error(error=error, code=401)

    def paginate_data(self, request, query_set, object_serializer=None, serializer_context=None):
        """
        :param request: django的request
        :param query_set: django model的query set或者其他list like objects
        :param object_serializer: 用来序列化query set, 如果为None, 则直接对query set切片
        :return:
        """
        try:
            limit = int(request.GET.get("limit", "10"))
        except ValueError:
            limit = 10
        if limit < 0 or limit > 250:
            limit = 10
        try:
            offset = int(request.GET.get("offset", "0"))
        except ValueError:
            offset = 0
        if offset < 0:
            offset = 0
        results = query_set[offset:offset + limit]
        if object_serializer:
            count = len(query_set)
            results = object_serializer(results, many=True, context=serializer_context).data
        else:
            count = len(query_set)
        data = {"results": results,
                "total": count}
        return data

    def get_user_profile(self, request):
        """返回None或者登录的UserProfile对象，用于那些不强制登录的视图获取登录者"""

        url = settings.USER_CENTER_GATEWAY + '/api/verify'
        headers = {'authorization': request.META.get("HTTP_AUTHORIZATION")}
        try:
            res = requests.get(url=url, headers=headers)
            res_data = res.json()
            me = UserProfile.objects.get(uid=res_data['data'])
        except:
            me = None
        return me
