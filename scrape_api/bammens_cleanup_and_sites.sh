#!/bin/bash

# The complete import process of bammens
# used for testing / developing / debugging locally

set -xue

# assumes we scraped the raw bammens data.

# step 2 cleanup
python bammens/copy_to_django.py wells --cleanup
python bammens/copy_to_django.py containers --wastename
python bammens/copy_to_django.py containers --cleanup

# step 2.1 copy to django models
python bammens/copy_to_django.py container_types
python bammens/copy_to_django.py wells
python bammens/copy_to_django.py containers

# now link the containers to the wells
python bammens/copy_to_django.py wells --link_containers
python bammens/copy_to_django.py wells --link_gebieden
python bammens/copy_to_django.py containers --geoview

# Validate import counts
python bammens/copy_to_django.py containers --validate


# step 3 create the sites.

# now create the sites.

python bammens/create_sites.py --fill_rd
python bammens/create_sites.py --merge_bgt
python bammens/create_sites.py --qa_wells
python bammens/create_sites.py --pand_distance
python bammens/create_sites.py --clusters
python bammens/create_sites.py --validate

python bammens/create_sites.py --sitefracties

# set bbga data
python bammens/buurt_count.py

# Kilogram statisiek.
python bammens/create_sites.py --kilostats
python bammens/create_sites.py --buurtcontainercounts
python bammens/create_sites.py --validate
