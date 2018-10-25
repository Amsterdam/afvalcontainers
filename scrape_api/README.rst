Download data from Bammens API
=================================================

author: Stephan Preeker.

About
------

- scraper for bammens.nl API the main maintenance CMS garbadge
  containers.
- provide cleanup script to add data to django rest api
- build sites of wells/containers
- scraper for kilogram.nl weigh data.

- Last: Provide the cleaned data as API.  https://api.data.amsterdam.nl/afval/

- NOTE/TOP in the deploy directory are the scripts which contain
  the last working version of import sript.

- NOTE keep the django models and sqlalchemy models in sync.

Instructions Bammens
---------------------

set env `BAMMENS_USER` to APIeelke (bammens api user in rattic)
set env `BAMMENS_PASSWORD` you can find it in rattic/password management

::
        export BAMMENS_USER=username
        export BAMMENS_PASSWORD=lookthisupinrattic

::
        docker-compose up database

        pip install -r requirements.txt

# create database tables

::
        python models.py

# now you can run:
# unfortunately this is rather slow on the bammens side.
# if we hammer the server too much production problems
# occur!

::
        python bammens/slurp_bammens.py containers
        python bammens/slurp_bammens.py wells
        python bammens/slurp_bammens.py containertypes

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

you can run bash `import_local.sh` or:

::
        python bammens/copy_to_django.py wells --cleanup
        python bammens/copy_to_django.py containers --cleanup
        python bammens/copy_to_django.py container_types
        python bammens/copy_to_django.py wells
        python bammens/copy_to_django.py containers

# now link the containers to the wells

::
        python bammens/copy_to_django.py wells --link_containers
        python bammens/copy_to_django.py wells --link_gebieden
        python bammens/copy_to_django.py containers --geoview

# now create the sites.

::
        python bammens/create_sites.py --fill_rd
        python bammens/create_sites.py --merge_bgt
        python bammens/create_sites.py --qa_wells
        python bammens/create_sites.py --pand_distance
        python bammens/create_sites.py --clusters
        python bammens/create_sites.py --validate


Instructions Kilogram
---------------------

# Kilogram can work on its own kilogram database.
# use environment variables to over ride:
# if not given will use afval container database.

::
      DATABASE_KILOGRAM_PASSWORD: insecure
      DATABASE_KILOGRAM_NAME: kilogram
      DATABASE_KILOGRAM_HOST:
      DATABASE_KILOGRAM_USER: kilogram
      DATABASE_KILOGRAM_PORT: 5432


#  create target tabels drop is optional.

::
        python kilogram/models.py --drop

set the kilogram.nl password.

::
        export KILOGRAM_API_PASSWORD=(look in rattic)

load current map / neighborhood data

::
        python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden buurt_simple,stadsdeel 4326 --db kilogram

# get latest and greatest of kilogram.nl

::

        python kilogram/slurp.py


# copy data into final table for serving to django

::
        python kilogram/copy_to_model.py
        python kilogram/copy_to_model.py --link_gebieden
        python kilogram/copy_to_model.py --fix_perscontainers

DONE!

Tests
======

`cd` into scrape_api

::
        export PYTHONPATH=.

        pytest
