# SciGWS
GeoWeb Services on Top of SciDB

## Installation

1. Clone this repository
> git clone https://github.com/gqueiroz/scigws.git

2. Navigate to scigws/src/server and run **/venv/venv.sh** and activate the enviroment
> cd scigws/src/
> ./venv/venv.sh
> source venv/bin/activate

3. Change/check SCIDB_VERSION and Database config on **server/settings.py
> SCIDB_VERSION = "14.3"
> DATABASES = {
>    'default': {
>        'ENGINE': 'django.db.backends.postgresql_psycopg2',
>        'NAME': 'modis_metadata',
>        'USER': 'postgres',
>        'PASSWORD': '',
>        'HOST': '127.0.0.1',
>        'PORT': '5433',
>    }
> }

4. Initialize the database migration models
> python manage.py migrate

5. Run the scidb django command. **Be sure that the scidb is running**
> python manage.py scidb

6. Start django developement server
> python manage.py runserver