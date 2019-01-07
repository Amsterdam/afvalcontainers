#!/usr/bin/env bash

# Import sidcon live weeg en vullgraad gegevens.

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

DIR=`dirname "$0"`

dc() {
	docker-compose -p enevocontainers${ENVIRONMENT} -f ${DIR}/docker-compose-kilo.yml $*
}

ENV="acceptance"
if [ "$ENVIRONMENT" == "production" ]; then
  ENV="production"
fi

trap 'dc kill ; dc down ; dc rm -f' EXIT

echo "Building / pull / cleanup images"
dc down
dc rm -f
dc pull
dc build

# create LIVE database tables if not exists.
if [ "$DROP" = "yes" ]
then
   dc run --rm importer python enevo/models.py --drop --live
else
   dc run --rm importer python enevo/models.py --live
fi

dc run --rm importer python enevo/slurp.py fill_levels
dc run --rm importer python enevo/convert_live_raw.py

dc down -v
