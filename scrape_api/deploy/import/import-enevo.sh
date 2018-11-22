#!/bin/sh

# We doen deze import los van de cleanup. want
# bammens.nl is erg traag.

set -e
set -u
set -x

export PYTHONPATH=/app/

DIR="$(dirname $0)"

dc() {
	docker-compose -p scrapeenevo${ENVIRONMENT} -f ${DIR}/docker-compose.yml $*
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
dc run importer /app/deploy/docker-wait.sh

echo "Importing data into database"

# Create all tables / database stuff
dc run --rm api python manage.py migrate
dc run --rm importer python enevo/models.py

# importeer buurt/stadseel
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden buurt_simple,stadsdeel 28992

# Importeer enevo api endpoints
dc run --rm importer python enevo/slurp.py sites
dc run --rm importer python enevo/slurp.py site_content_types
dc run --rm importer python enevo/slurp.py container_types
dc run --rm importer python enevo/slurp.py container_slots
dc run --rm importer python enevo/slurp.py containers
dc run --rm importer python enevo/slurp.py alerts

# Insert data into django database
dc run --rm importer python enevo/copy_to_django.py sites
dc run --rm importer python enevo/copy_to_django.py site_content_types
dc run --rm importer python enevo/copy_to_django.py container_types
dc run --rm importer python enevo/copy_to_django.py container_slots
dc run --rm importer python enevo/copy_to_django.py containers
dc run --rm importer python enevo/copy_to_django.py alerts

# backup raw data for debuging
dc exec -T database backup-db.sh afvalcontainers

dc run --rm importer python -m objectstore.databasedumps /backups/database.dump db_slurp --upload-db
dc run --rm importer python -m objectstore.databasedumps /backups/database.dump db_slurp --days 20

echo "Remove containers and volumes."
dc down -v
dc rm -f

echo "Done"

