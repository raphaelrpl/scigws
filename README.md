# SciGWS
GeoWeb Services on Top of SciDB

### Installation

Clone this repository
```bash
git clone https://github.com/gqueiroz/scigws.git
```

Navigate to scigws/src/server and run **/venv/venv.sh** and activate the enviroment
```bash
cd scigws/src/
./venv/venv.sh
source venv/bin/activate
```

Change/check SCIDB_VERSION and Database config on **server/settings.py**
```python
SCIDB_VERSION = "14.3"
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'modis_metadata',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5433',
    }
}
```

Initialize the database migration models
```bash
python manage.py migrate
```

Run the scidb django command. **Be sure that the scidb is running**
```bash
python manage.py scidb
```

Start django developement server
```bash
python manage.py runserver
```