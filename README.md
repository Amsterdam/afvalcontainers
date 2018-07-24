# Afvalcontainers #


## Scrape API ##

Python script to download all the containers, containertypes and wells from https://bammensservice.nl api

Swagger documentation can be found here after you login: https://bammensservice.nl/api/doc

### Install procedure ###

```
git clone https://github.com/Amsterdam/afvalcontainers.git afvalcontainers
cd afvalcontainers
```
Before you can use the api you must create the login environment variables
```
export CKAN_API_KEY=****
export BAMMENS_API_USERNAME=****
export BAMMENS_API_PASSWORD=****
```

Start the docker database and run the download en upload scripts.
```
docker-compose build
docker-compose up
```

#### Local development ####

Create a local environment and activate it:
```
virtualenv --python=$(which python3) venv
source venv/bin/activate
```
To run the downloader and uploader to Postgres in a docker you can use this command:
```
docker-compose build database
docker-compose up database
```

Run the uploader to postgres locally with stating the folder and postgres login and port where to write to.
```
python load_json2pg.py data dev
```

To create the geojson run:
```
python json2geojson.py data dev
```

To upload the geojson to the CKAN store:
```
python load_file_to_ckan.py https://api.data.amsterdam.nl/catalogus afvalcontainers data/afvalcontainers.geojson
```
