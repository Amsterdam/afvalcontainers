Afvalcontainers
=============


provides the WFS services with the actual parkingsport dataset

- all containers.
- all wells.

Docker Installation
===================

::
   docker-compose build
   docker-compose up


Manual Installation
===================


 1. Create a afvalcontainers database.

 2. Add the postgis extension

::
    CREATE EXTENSION postgis;

Create the tables
=================

::
    python3 manage.py migrate

Load the data
=============

::
    See instructions in scrape_api README.


For local datapunt developement/developers

docker-compose database update-db.sh afvalcontainers


remove old geoviews:

::
    python manage.py migrate geo_views zero

create geoviews:

::

    python manage.py migrate geo_view

test
