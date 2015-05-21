from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from apps.scidb.db import SciDB
from apps.scidb.exception import SciDBConnectionError
from json import loads


class Command(BaseCommand):
    help = 'A scidb command that store dummy data on SciDB and PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument('--host', dest='host', default="localhost",
                            help='Type SciDB host: default is localhost')
        parser.add_argument('--port', dest='port', default=1239,
                            help='Type SciDB host: default is localhost')

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

        self.stdout.write("Preparing to load PostgreSQL metadata")
        call_command("loaddata", "apps/geo/fixtures/initial.json")

        self.stdout.write('Command successfully')