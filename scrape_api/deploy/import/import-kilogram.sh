#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/

DIR="$(dirname $0)"

dc() {
	docker-compose -p kilogram${ENVIRONMENT} -f $(DIR)/docker-compose-kilo.yml $*
}

trap 'dc kill ; dc rm -f' EXIT

dc rm -f
dc pull
dc build

# create database tables if not exists.
if [ "$DROP" = "yes" ]
then
   dc run --rm importer python kilogram/models.py --drop
else
   dc run --rm importer python kilogram/models.py
fi

# load current map / neighborhood data
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden buurt_simple,stadsdeel 4326 --db kilogram

# slurp latest and greatest of kilogram.nl
dc run --rm importer python kilogram/slurp.py

# copy data into final table for serving to django
dc run --rm importer python kilogram/copy_to_model.py

# add gebieden data to endpoint
dc run --rm importer python kilogram/copy_to_model.py --link_gebieden
