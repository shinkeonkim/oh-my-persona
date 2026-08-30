from djangorestframework_camel_case.util import underscoreize


class CamelCaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.GET:
            request.GET = underscoreize(request.GET.dict())
        return self.get_response(request)
