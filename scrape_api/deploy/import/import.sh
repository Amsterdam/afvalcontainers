#!/bin/sh

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

dc run --rm api python manage.py migrate
dc run --rm importer python models.py

# importeer buurt/stadseel
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden buurt_simple,stadsdeel 28992


# Importeer bammens api endpoints
dc run --rm importer python slurp_api.py container_types
dc run --rm importer python slurp_api.py containers
dc run --rm importer python slurp_api.py wells

# Opschonen
dc run --rm importer python copy_to_django.py wells --cleanup
dc run --rm importer python copy_to_django.py containers --wastename
dc run --rm importer python copy_to_django.py containers --cleanup

# Kopieren containers to django tables
dc run --rm importer python copy_to_django.py container_types
dc run --rm importer python copy_to_django.py wells
dc run --rm importer python copy_to_django.py containers

# Link containers to wells
dc run --rm importer python copy_to_django.py containers --link_containers

# Link wells to gebieden
dc run --rm importer python copy_to_django.py wells --link_gebieden
dc run --rm importer python copy_to_django.py containers --geoview

# Validate import counts
dc run --rm importer python copy_to_django.py containers --validate

echo "Running backups"
dc exec -T database backup-db.sh afvalcontainers

dc run --rm importer python -m objectstore.databasedumps /backups/database.dump dbdumps --upload-db

echo "Remove containers and volumes."
dc down -v
dc rm -f

echo "Done"
