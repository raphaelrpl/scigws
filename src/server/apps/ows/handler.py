class ServiceMeta(type):
    params = {}


class ServiceRequest(object):
    __metaclass__ = ServiceMeta

    def __init__(self, **params):
        pass

a = ServiceRequest(name="Abacate", service="WCS")


class RequestHandler(object):
    @classmethod
    def handle(cls, request):
        """ output xml """
        params = {}
        if request.method == "POST":
            pass  # fix
        elif request.method == "GET":
            params = request.GET



class OWSExceptionHandler(object):
    @classmethod
    def handle(cls, request, exception):
        pass