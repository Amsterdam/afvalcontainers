#!/bin/sh

# We doen deze import los van de cleanup. want
# bammens.nl is erg traag.

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
	docker-compose -p scrapebammens${ENVIRONMENT} -f ${DIR}/docker-compose.yml $*
}

trap 'dc kill ; dc rm -f' EXIT

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
dc run importer /app/deploy/docker-wait.sh

echo "Importing data into database"

# Create all tables / database stuff
dc run --rm api python manage.py migrate
dc run --rm importer python bammens/models.py

# importeer buurt/stadseel
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden buurt_simple,stadsdeel 28992

# Importeer bammens api endpoints
dc run --rm importer python bammens/slurp_bammens.py container_types
dc run --rm importer python bammens/slurp_bammens.py containers
dc run --rm importer python bammens/slurp_bammens.py wells

# backup raw data for debuging
dc exec -T database backup-db.sh afvalcontainers

dc run --rm importer python -m objectstore.databasedumps /backups/database.dump db_slurp --upload-db
dc run --rm importer python -m objectstore.databasedumps /backups/database.dump db_slurp --days 20

echo "Remove containers and volumes."
dc down -v
dc rm -f

echo "Done"
