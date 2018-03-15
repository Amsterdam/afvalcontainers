set -x
set -u
set -e

python /app/load_file_to_ckan.py https://api.data.amsterdam.nl/catalogus afvalcontainers /tmp/afvalcontainers.geojson

