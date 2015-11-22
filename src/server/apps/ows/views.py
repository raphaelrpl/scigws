from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from handler import RequestHandler, OWSExceptionHandler

from datetime import datetime


class OWSView(View):
    def process_request(self, request):
        code = 200
        try:
            st = datetime.now()
            operation = RequestHandler.handle(request)
            # Set value to encoder and prepare it to be serialized
            operation.process(request)
            ed = datetime.now() - st
            print("Req -> " + str(ed))
            return HttpResponse(operation.response().serialize(), content_type=operation.response().content_type, status=code)
        except Exception as e:
            exception = OWSExceptionHandler.handle(e)
            code = 400
            return HttpResponse(exception.serialize(), content_type=exception.content_type, status=code)

    def get(self, request):
        return self.process_request(request)

    @csrf_exempt
    def post(self, request):
        return self.process_request(request)
