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

# load BGT objects of everything on the ground.
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

echo "Importing data into database"

dc run --rm api python manage.py migrate
dc run --rm importer python models.py

# importeer buurt/stadseel/pand/verblijfsobject informatie.
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden buurt_simple,stadsdeel 4326
dc run --rm importer python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/bag verblijfsobjecten,pand 4326


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

echo "Remove containers and volumes."
dc down -v
dc rm -f

echo "Done"
