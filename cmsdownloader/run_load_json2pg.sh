set -x
set -u
set -e

python /app/load_json2pg.py /tmp config.ini docker

