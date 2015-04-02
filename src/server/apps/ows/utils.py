from exception import OWSIOError
from json import loads


def get_scidb_credentials():
    config = {"host": "localhost", "port": 1239}
    try:
        with open("config/db.config.json") as data:
            config = loads(data.read()).get('scidb', {})
    except IOError:
        pass
    return config


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args)
        return cls._instance


class Meta(Singleton):
    data = None

    def __init__(self, path):
        try:
            with open(path) as f:
                self.data = loads(f.read())
        except IOError as e:
            raise OWSIOError(e)


class Identification(Meta):
    def __init__(self, path="config/metadata.json"):
        super(Identification, self).__init__(path)


class DBConfig(Meta):
    def __init__(self, path="config/db.config.json"):
        super(DBConfig, self).__init__(path)


class GeoArray(Meta):
    def __init__(self, path="config/db.config.json"):
        super(GeoArray, self).__init__(path)