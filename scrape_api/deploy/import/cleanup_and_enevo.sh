#!/bin/bash

# We created an extra cleanup scrips because the import can only run in the
# night. so we can run this in a seperate task process.

# site creation script / cleanup. should run after import is done

set -e
set -u
set -x

export PYTHONPATH=/app/


DIR="$(dirname $0)"

dc() {
	docker-compose -p cleanup${ENVIRONMENT} -f ${DIR}/docker-compose.yml $*
}

trap 'dc down ; dc rm -f' EXIT

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
dc run --rm importer python -m objectstore.databasedumps /data db_slurp --download-db

ENV="acceptance"
if [ "$ENVIRONMENT" == "production" ]; then
  ENV="production"
fi

dc exec -T database pg_restore --no-privileges --no-owner --if-exists -j 4 -c -C -d postgres -U afvalcontainers /data/database.$ENV


# importeer buurt/stadseel
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden buurt_simple,stadsdeel 28992

# Sometimes the migrations could be behind.. since we could load older data
dc run --rm api python manage.py migrate

# Opschonen
dc run --rm importer python bammens/copy_to_django.py wells --cleanup
dc run --rm importer python bammens/copy_to_django.py containers --wastename
dc run --rm importer python bammens/copy_to_django.py containers --cleanup


# Kopieren containers to django tables
dc run --rm importer python bammens/copy_to_django.py container_types
dc run --rm importer python bammens/copy_to_django.py wells
dc run --rm importer python bammens/copy_to_django.py containers

# Link containers to wells
dc run --rm importer python bammens/copy_to_django.py containers --link_containers

# Link wells to gebieden
dc run --rm importer python bammens/copy_to_django.py wells --link_gebieden
dc run --rm importer python bammens/copy_to_django.py containers --geoview

# Validate import counts
dc run --rm importer python bammens/copy_to_django.py containers --validate

# Import ENEVO API

dc run --rm importer python enevo/models.py
# Importeer enevo api endpoints
dc run --rm importer python enevo/slurp.py content_types
dc run --rm importer python enevo/slurp.py sites
dc run --rm importer python enevo/slurp.py site_content_types
dc run --rm importer python enevo/slurp.py container_types
dc run --rm importer python enevo/slurp.py container_slots
dc run --rm importer python enevo/slurp.py containers
# dc run --rm importer python enevo/slurp.py alerts

# Insert data into django ENEVO database tables
dc run --rm importer python enevo/copy_to_django.py content_types
dc run --rm importer python enevo/copy_to_django.py sites
dc run --rm importer python enevo/copy_to_django.py site_content_types
dc run --rm importer python enevo/copy_to_django.py container_types
dc run --rm importer python enevo/copy_to_django.py container_slots
dc run --rm importer python enevo/copy_to_django.py containers

dc run --rm importer python enevo/copy_to_django.py container_slots --link_container_slots
dc run --rm importer python enevo/copy_to_django.py containers --validate_containers

echo "Running backups"
dc exec -T database backup-db.sh afvalcontainers

echo "Store DB dump in objectstore for site creation step"
dc run --rm importer python -m objectstore.databasedumps /backups/database.dump db_dumps --upload-db
dc run --rm importer python -m objectstore.databasedumps /backups/database.dump db_dumps --days 20
