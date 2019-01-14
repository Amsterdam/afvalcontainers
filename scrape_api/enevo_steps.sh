#!/bin/bash

# The complete import process of enevo
# used for testing / developing / debugging locally

set -xue

python enevo/slurp.py content_types
python enevo/slurp.py container_types
python enevo/slurp.py container_slots
python enevo/slurp.py containers
python enevo/slurp.py sites
python enevo/slurp.py site_content_types
# python enevo/slurp.py alerts
# python enevo/slurp.py fill_levels


python enevo/copy_to_django.py content_types
python enevo/copy_to_django.py sites
python enevo/copy_to_django.py site_content_types
python enevo/copy_to_django.py container_types
python enevo/copy_to_django.py container_slots
python enevo/copy_to_django.py containers

# python enevo/copy_to_django.py alerts

python enevo/copy_to_django.py container_slots --link_container_slots
python enevo/copy_to_django.py containers --validate_containers
