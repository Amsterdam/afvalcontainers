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
dc build
dc pull

# create database tables if not exists.
if [ "$DROP" = "yes" ]
then
   dc run --rm importer python enevo/models.py --drop  --live
else
   dc run --rm importer python enevo/models.py --live
fi

# slurp latest and greatest of kilogram.nl
dc run --rm importer python enevo/slurp.py fill_levels
# copy data into final table for serving to django

dc run --rm importer python enevo/convert_live_raw.py

dc down -v
