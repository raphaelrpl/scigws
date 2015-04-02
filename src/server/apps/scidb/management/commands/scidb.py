from django.core.management.base import BaseCommand, CommandError, make_option
from apps.scidb.db import SciDB
from apps.scidb.exception import SciDBConnectionError
from json import loads


class Command(BaseCommand):
    help = 'A command for init test data on SciDB'
    option_list = BaseCommand.option_list + (
        make_option('--host', action='store_true', dest='host', default="localhost",
                    help="Type SciDB host: default is localhost"),
        make_option('--port', action='store_true', dest='port', default=1239,
                    help="Type SciDB port: default is 1239"),)

    def handle(self, *args, **options):
        host = options.get('host')
        port = int(options.get('port'))
        try:
            connection = SciDB(str(host), port)
            with open("config/scidb-data.json") as f:
                commands = loads(f.read())
        except SciDBConnectionError as e:
            raise CommandError(e.message)
        except IOError as e:
            raise CommandError(e.message)
        for command in commands:
            result = connection.executeQuery(str(command['afl']), "AFL")
            connection.completeQuery(result.queryID)
            self.stdout.write("Done inserting %s data" % command.get('name', "ARRAY"))
        self.stdout.write('Command successfully')