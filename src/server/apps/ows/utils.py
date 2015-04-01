import json


def get_scidb_credentials():
    config = {"host": "localhost", "port": 1239}
    try:
        with open("config/db.config.json") as data:
            config = json.loads(data.read()).get('scidb', {})
    except IOError:
        pass
    return config
