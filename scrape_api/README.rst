Download data from Bammens API
=================================================

author: Stephan Preeker.

About
------

- iohttp scraper for bammens api about garbadge
  containers inserts data directly into database
- provide cleanup script to add data to django rest api


Instructions
------------

set `BAMMENS_USER` to acceptance of production
set `BAMMENS_PASSWORD` you can find it in rattic/password management

::
        docker-compose up database

        pip install -r requirements.txt

# create database tables

::
        python models.py

# now you can run:

::
        python slurp_api.py containers
        python slurp_api.py wells
        python slurp_api.py containertypes

# takes about 30 mins.

# Data is now stored in tables, with a raw data json field.
# ready for further processing

# For the API.

# In the api/src directory

::
        pip install -r requirements.txt

# In the api/src/afvalcontainers

::
        python manage.py migrate


# In the scrape_api/ directory, if everything is downloaded

::
        python copy_to_django.py wells --cleanup
        python copy_to_django.py containers --cleanup
        python copy_to_django.py container_types
        python copy_to_django.py wells
        python copy_to_django.py containers

# now link the containers to the wells

::
        python copy_to_django.py wells --linkcontainers

Tests
======

`cd` into scrape_api

::
        export PYTHONPATH=.

        pytest
