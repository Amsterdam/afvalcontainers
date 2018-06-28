#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
	docker-compose $*
}

# dc exec -T database update-table.sh bag bag_buurt public afvalcontainers
# load BGT objects of everything on the ground.
dc exec -T database update-table.sh basiskaart BGT_OWGL_verkeerseiland bgt afvalcontainers spreeker
dc exec -T database update-table.sh basiskaart BGT_OWGL_berm bgt afvalcontainers spreeker
dc exec -T database update-table.sh basiskaart BGT_OTRN_open_verharding bgt afvalcontainers spreeker
dc exec -T database update-table.sh basiskaart BGT_OTRN_transitie bgt afvalcontainers spreeker
dc exec -T database update-table.sh basiskaart BGT_WGL_fietspad bgt afvalcontainers spreeker
dc exec -T database update-table.sh basiskaart BGT_WGL_voetgangersgebied bgt afvalcontainers spreeker
dc exec -T database update-table.sh basiskaart BGT_WGL_voetpad bgt afvalcontainers spreeker
# load BGT road objects of everything on the ground.
dc exec -T database update-table.sh basiskaart BGT_WGL_parkeervlak bgt afvalcontainers spreeker
dc exec -T database update-table.sh basiskaart BGT_WGL_rijbaan_lokale_weg bgt afvalcontainers spreeker
dc exec -T database update-table.sh basiskaart BGT_WGL_rijbaan_regionale_weg bgt afvalcontainers spreeker
