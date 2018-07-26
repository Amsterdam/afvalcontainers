#!/bin/sh

# We created an extra cleanup scrips because the import can only run in the
# night. so we can run this in a seperate task process.

# site creation script / cleanup. should run after import is done

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
	docker-compose -p scrapebammens${ENVIRONMENT} -f ${DIR}/docker-compose.yml $*
}

# trap 'dc kill ; dc rm -f' EXIT

# For database backups:
rm -rf ${DIR}/backups
mkdir -p ${DIR}/backups

# dc down	-v
# dc rm -f
# dc pull

echo "Building images"
dc build

echo "Bringing up and waiting for database"
dc up -d database
dc run importer /app/deploy/docker-wait.sh

dc exec -T database touch /data/test.txt

# Download latest dump from objectstore
dc run --rm importer python -m objectstore.databasedumps /data db_dumps --download-db
ENV='ACCEPTANCE'
if [$ENVIRONMENT = 'production']; then
   ENV='PRODUCTION'
fi

dc exec -T database pg_restore --no-privileges --no-owner --if-exists -j 4 -c -C -d postgres -U postgres /data/database.$ENV

# get the latest imported database
dc exec -T database update-db.sh afvalcontainers

# load BGT objects of everything related to containers on the ground.
dc exec -T database update-table.sh basiskaart BGTPLUS_BAK_afval_apart_plaats bgt afvalcontainers spreeker

dc exec -T database update-table.sh basiskaart BGT_OWGL_verkeerseiland bgt afvalcontainers
dc exec -T database update-table.sh basiskaart BGT_OWGL_berm bgt afvalcontainers
dc exec -T database update-table.sh basiskaart BGT_OTRN_open_verharding bgt afvalcontainers
dc exec -T database update-table.sh basiskaart BGT_OTRN_transitie bgt afvalcontainers
dc exec -T database update-table.sh basiskaart BGT_WGL_fietspad bgt afvalcontainers
dc exec -T database update-table.sh basiskaart BGT_WGL_voetgangersgebied bgt afvalcontainers
dc exec -T database update-table.sh basiskaart BGT_WGL_voetpad bgt afvalcontainers

dc exec -T database update-table.sh basiskaart BGT_WGL_parkeervlak bgt afvalcontainers
dc exec -T database update-table.sh basiskaart BGT_WGL_rijbaan_lokale_weg bgt afvalcontainers
dc exec -T database update-table.sh basiskaart BGT_WGL_rijbaan_regionale_weg bgt afvalcontainers

dc exec -T database update-table.sh basiskaart BGT_BTRN_groenvoorziening bgt afvalcontainers
dc exec -T database update-table.sh basiskaart BGT_OTRN_onverhard bgt afvalcontainers
dc exec -T database update-table.sh basiskaart BGT_OTRN_erf bgt afvalcontainers

# get verblijfsobjecten/nummeraanduidingen.
# dc exec -T database update-table.sh bag bag_nummeraanduiding public afvalcontainers
dc exec -T database update-table.sh bag bag_verblijfsobject public afvalcontainers

# importeer buurt/stadseel
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden buurt_simple,stadsdeel 28992

# importeer buurt/stadseel/pand/verblijfsobject informatie.
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/bag openbareruimte 28992
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/bag verblijfsobject 28992
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/bag pand 28992

# create all tables if missing
dc run --rm importer python models.py

dc run --rm importer python create_sites.py --merge_bgt
dc run --rm importer python create_sites.py --qa_wells
dc run --rm importer python create_sites.py --pand_distance
dc run --rm importer python create_sites.py --clusters

echo "Running backups"
dc exec -T database backup-db.sh afvalcontainers

echo "Store DB dump in objectstore for cleanup step"
dc run --rm importer python -m objectstore.databasedumps /backups/database.dump db_cleaned --upload-db
