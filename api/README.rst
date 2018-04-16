Parkeervakken
=============

Imports parkeervakken shape file into database.
provides the WFS services with the actual parkingsport dataset

- ALL parking spots.
- parking spot data like (FISCAAL / MULDER) ficscaal means non free spots. Mulder are spots for handicaped people.
- TVM ( tijdelijke verkeersmaatregelen ) dataset.
- park sign information. (Electric / laden lossen etc)

NO WEB API YET besides a mapserver wfs.


Docker Installation
===================

::
   docker-compose build
   docker-compose up


Manual Installation
===================


 1. Create a parkeervakken database.

 2. Add the postgis extension

::
    CREATE EXTENSION postgis;

Create the tables
=================

::
    python3 import_data.py --user postgres --password insecure --host 127.0.0.1 --port 5409 --database parkeervakken initialize

Load the data
=============

::
    python3 import_data.py --user postgres --password insecure --host 127.0.0.1 --port 5409 --database parkeervakken update  --source PWD


The data pipeline overview
==========================

 1. Raw shapefiles get loaded in the 'his' schema.

 2. Some business logic and transformations are applied in the  'bm' schema

 3. In the 'bv' (Business View) provides the latest data
    now it is possible to query per day the reservations

 4. A geoview is created for the mapserver


remove old geoviews:

::
    python manage.py migrate geo_views zero

create geoviews:

::

    python manage.py migrate geo_view

test
