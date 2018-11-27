Scrape kilogram.nl portal API for accurate measurements.


Set the PYTHONPATH in to the scrape_api directory of the project:

python kilogram/models.py to create database models
python kilogram/slurp.py to download latest data
python kilogram/copy_to_model.py to convert raw api data into

# add gebieden data to endpoint
python kilogram/copy_to_model.py --link_gebieden

# Do a correction for perscontainers they only have a
# second weigh data filled
python kilogram/copy_to_model.py --fix_perscontainers

database table to be served by the API project.
