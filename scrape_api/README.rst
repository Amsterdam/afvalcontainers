Download data from Bammens API
=================================================

author: Stephan Preeker.

About.
------

iohttp scraper for bammens api about garbadge containers
inserts data directly into database


Instructions.
---------------

set `BAMMENS_USER` to acceptance of production
set `BAMMENS_PASSWORD` you can find it in rattic/password management

        docker-compose up database

        pip install -r requirements.txt

# create database tables

        python models.py

# now you can run:

        python slurp_api.py containers
        python slurp_api.py wells
        python slurp_api.py containertypes

# Data is now stored in tables, with a raw data json field.
# ready for further processing


Tests
======

`cd` into scrape_api

        export PYTHONPATH=.

        pytest
