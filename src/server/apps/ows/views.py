from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from handler import RequestHandler, OWSExceptionHandler


class OWSView(View):
    def process_request(self, request):
        code = 200
        try:
            result = RequestHandler.handle(request)
            data = result.encode(request)
            if result.content_type == "application/xml":
                return HttpResponse(result.serialize(data),
                                    content_type=result.content_type, status=code)
            # It should be an image
            return HttpResponse(open(data), content_type=result.content_type, status=code)
        except Exception as e:
            result, content_type = OWSExceptionHandler.handle(e)
            code = 400
            return HttpResponse(result, content_type=content_type, status=code)

    def get(self, request):
        return self.process_request(request)

    @csrf_exempt
    def post(self, request):
        return self.process_request(request)