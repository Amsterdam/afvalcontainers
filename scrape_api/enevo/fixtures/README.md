Scrape enevo.nl API for fill data.


Set the PYTHONPATH in to the scrape_api directory of the project:

python enevo/models.py to create database models
python enevo/slurp.py with one of the several endpoints to download latest data e.g: containers, sites, container_slots etc..
python enevo/copy_to_model.py to convert raw api data into (WIP)
database table to be served by the API project. (WIP)

