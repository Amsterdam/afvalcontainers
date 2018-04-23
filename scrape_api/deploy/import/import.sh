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

echo "For debugging list volumes"
dc down	-v
dc rm -f
dc pull

docker volume ls

echo "Building images"
dc build

echo "Bringing up and waiting for database"
dc up -d database
dc run importer /deploy/docker-wait.sh

dc exec -T database update-table.sh bag bag_buurt public afvalcontainers

echo "Importing data into database"

dc run --rm importer python models.py
# importeer alle objectstore bronnen
dc run --rm importer python scrape_api container_types
dc run --rm importer python scrape_api containers
dc run --rm importer python scrape_api wells

dc run --rm importer python copy_to_django wells --cleanup
dc run --rm importer python copy_to_django containers --cleanup
dc run --rm importer python copy_to_django containers
dc run --rm importer python copy_to_django wells
dc run --rm importer python copy_to_django container_types
# link containers to wells
dc run --rm importer python copy_to_django containers --linkcontainers


echo "Running backups"
dc exec -T database backup-db.sh afvalcontainers

echo "Remove containers and volumes."
dc down -v
dc rm -f

echo "Done"
