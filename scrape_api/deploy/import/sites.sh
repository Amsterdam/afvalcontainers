#!/bin/bash

# We created an extra cleanup scrips because the import can only run in the
# night. so we can run this in a seperate task process.

# site creation script / cleanup. should run after import is done

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
	docker-compose -p sitescontainers${ENVIRONMENT} -f ${DIR}/docker-compose.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

# For database backups:
rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

dc down	-v
dc rm -f
dc pull

echo "Building images"
dc build

echo "Bringing up and waiting for database"
dc up -d database
dc run --rm importer /app/deploy/docker-wait.sh

dc exec -T database touch /data/test.txt

# Download latest dump from objectstore
dc run --rm importer python -m objectstore.databasedumps /data db_enevo --download-db


ENV="acceptance"
if [[ "$ENVIRONMENT" == "production" ]]; then
  ENV="production"
fi


dc exec -T database pg_restore --no-privileges --no-owner --if-exists -j 4 -c -C -d postgres -U afvalcontainers /data/database.$ENV

# Sometimes the migrations could be behind.. since we could load older data
dc run --rm api python manage.py migrate

update_table() {
	# add your DP username behind this command to allow local development.
	dc exec -T database update-table.sh $*
}

# load BGT objects of everything related to containers on the ground.
update_table basiskaart BGTPLUS_BAK_afval_apart_plaats bgt afvalcontainers

update_table basiskaart BGT_OWGL_verkeerseiland bgt afvalcontainers
update_table basiskaart BGT_OWGL_berm bgt afvalcontainers
update_table basiskaart BGT_OTRN_open_verharding bgt afvalcontainers
update_table basiskaart BGT_WGL_fietspad bgt afvalcontainers
update_table basiskaart BGT_WGL_voetgangersgebied bgt afvalcontainers
update_table basiskaart BGT_WGL_voetpad bgt afvalcontainers

update_table basiskaart BGT_WGL_parkeervlak bgt afvalcontainers
update_table basiskaart BGT_WGL_rijbaan_lokale_weg bgt afvalcontainers
update_table basiskaart BGT_WGL_rijbaan_regionale_weg bgt afvalcontainers
update_table basiskaart BGT_WGL_woonerf bgt afvalcontainers

update_table basiskaart BGT_BTRN_groenvoorziening bgt afvalcontainers
update_table basiskaart BGT_OTRN_onverhard bgt afvalcontainers
update_table basiskaart BGT_OTRN_erf bgt afvalcontainers

# get verblijfsobjecten/nummeraanduidingen.
# dc exec -T database update-table.sh bag bag_nummeraanduiding public afvalcontainers
update_table bag bag_verblijfsobject public afvalcontainers
update_table bag bag_pand public afvalcontainers
update_table bag bag_ligplaats public afvalcontainers

# restore kilogram weigh measurements (24h old)
# TODO do this on live database?
# dc exec -T database update-table.sh kilogram kilogram_weigh_measurement public afvalcontainers

# importeer buurt/stadseel
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden buurt_simple,stadsdeel 28992

# importeer buurt/stadseel/pand/verblijfsobject informatie.
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/bag openbareruimte 28992
# dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/bag verblijfsobject 28992
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/bag pand 28992


# create all tables if missing
dc run --rm importer python bammens/models.py

dc run --rm importer python bammens/create_sites.py --fill_rd
dc run --rm importer python bammens/create_sites.py --merge_bgt
dc run --rm importer python bammens/create_sites.py --qa_wells
dc run --rm importer python bammens/create_sites.py --pand_distance
dc run --rm importer python bammens/create_sites.py --clusters
dc run --rm importer python bammens/create_sites.py --sitefracties

# get bbga data
dc run --rm importer python bammens/buurt_count.py

# validation
dc run --rm importer python bammens/create_sites.py --validate

# crop the database from no longer needed data
dc run --rm importer python bammens/create_sites.py --cleanextra

echo "creating database dump"
dc exec -T database backup-db.sh afvalcontainers

echo "Store final DB dump in objectstore"
dc run --rm importer python -m objectstore.databasedumps /backups/database.dump db_cleaned --upload-db

dc down -v
