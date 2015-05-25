from django.core.management.commands.runserver import Command as RunServerCommand
from apps.scidb.db import SciDB
from apps.scidb.exception import SciDBConnectionError
from server import settings


class Command(RunServerCommand):
    help = 'A command to start development server on SciDB'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        credentials = getattr(settings, 'SCIDB_CONFIG', {})
        if not credentials or not isinstance(credentials, dict):
            raise ValueError("Error: Set SCIDB_CONFIG on settings.py. It must be a dict with host and port values")
        try:
            connection = SciDB(**credentials)
            connection.disconnect()
        except SciDBConnectionError as e:
            self.stdout.write("**** ERROR: Cannot connect to SciDB. Is it running? - Input: {0}".format(credentials))
            return

        super(Command, self).handle(*args, **options)