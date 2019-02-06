#!/usr/bin/env bash

# update kilogram statistiek weeg en vullgraad gegevens.

set -u   # crash on missing env variables
set -e   # stop on any error
set -x   # print what we are doing

DIR=`dirname "$0"`

dc() {
	docker-compose -p maintenance${ENVIRONMENT} -f ${DIR}/docker-compose-kilo.yml $*
}

ENV="acceptance"
if [ "$ENVIRONMENT" == "production" ]; then
  ENV="production"
fi

trap 'dc kill ; dc down -v ; dc rm -f' EXIT

echo "Building / pull / cleanup images"
dc rm -f
dc build
dc pull

# get latest bbga data
dc run --rm importer python bammens/buurt_count.py

# Importeer buurt/stadseel
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden buurt_simple,buurtcombinatie,gebiedsgerichtwerken,stadsdeel 28992 --db kilogram
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/afval container_coordinaten,well_coordinaten,site_circle,enevo_site_points 28992 --db kilogram

# Kilogram statisiek.
# dc run --rm importer python bammens/create_sites.py --kilostats
# dc run --rm importer python bammens/create_sites.py --buurtcontainercounts
