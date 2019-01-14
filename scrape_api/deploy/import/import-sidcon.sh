#!/usr/bin/env bash

# Import sidcon live weeg en vullgraad gegevens.

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

export PYTHONPATH=/app/

DIR=`dirname "$0"`

dc() {
	docker-compose -p sidconlive${ENVIRONMENT} -f $DIR/docker-compose-kilo.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

dc pull

# create database tables if not exists.
if [ "$DROP" = "yes" ]
then
   dc run --rm importer python sidcon/models.py --drop
else
   dc run --rm importer python sidcon/models.py
fi

# slurp latest and greatest of kilogram.nl
dc run --rm importer python sidcon/slurp_sidcon.py --slurp
# copy data into final table for serving to django

dc run --rm importer python sidcon/slurp_sidcon.py --copy
