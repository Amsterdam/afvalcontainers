
set -xue

python copy_to_django.py wells --cleanup
python copy_to_django.py containers --cleanup
python copy_to_django.py container_types
python copy_to_django.py wells
python copy_to_django.py containers

# now link the containers to the wells

python copy_to_django.py wells --link_containers
python copy_to_django.py wells --link_gebieden
python copy_to_django.py containers --geoview

# now create the sites.

python create_sites.py --fill_rd
python create_sites.py --merge_bgt
python create_sites.py --qa_wells
python create_sites.py --pand_distance
python create_sites.py --clusters
python create_sites.py --validate


