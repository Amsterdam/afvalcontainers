Scrape kilogram.nl portal API for accurate measurements.


Set the PYTHONPATH in to the scrape_api directory of the project:

python kilogram/models.py to create database models
python kilogram/slurp.py to download latest data
python kilogram/copy_to_model.py to convert raw api data into
database table to be served by the API project.
