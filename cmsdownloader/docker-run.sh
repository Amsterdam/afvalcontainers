set -x
set -u
set -e

/app/run_cmsdownloader.sh
/app/run_json2geojson.sh
/app/run_load_json2pg.sh
/app/run_load_file_to_ckan.sh
