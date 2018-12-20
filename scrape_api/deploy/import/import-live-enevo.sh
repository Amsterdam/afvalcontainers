#!/usr/bin/env bash

# Import sidcon live weeg en vullgraad gegevens.

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/

DIR=`dirname "$0"`

dc() {
	docker-compose -p liveenevo${ENVIRONMENT} -f $DIR/docker-compose-kilo.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

dc rm -f
dc pull
dc build

# create database tables if not exists.
if [ "$DROP" = "yes" ]
then
   dc run --rm importer python enevo/models.py fill_levels --drop
else
   dc run --rm importer python enevo/models.py fill_levels
fi

# load current map / neighborhood data
# dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden buurt_simple,stadsdeel 4326 --db kilogram

# slurp latest and greatest of kilogram.nl
dc run --rm importer python enevo/slurp_sidcon.py --slurp
# copy data into final table for serving to django

dc run --rm importer python enevo/slurp_sidcon.py --copy

# add gebieden data to endpoint

dc down -v
