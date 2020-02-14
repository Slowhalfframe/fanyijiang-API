import functools


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
