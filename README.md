# Afvalcontainers #


## Scrape API ##

Python script to download all the containers, containertypes and wells from https://bammensservice.nl api

Swagger documentation can be found here after you login: https://bammensservice.nl/api/doc

### Model Overview ###


                             +--------------------+
+-----------------+          |                    |
|      Type       +---------->     Container      |     Removable Container
+-----------------+          |                    |
                             +---------+----------+
                                       |
                                       |
                             +---------v----------+
                             |                    |
                             |        Well        |     Hole in the ground for container
                             |                    |
                             +---------+----------+
                                       |
                                       |
                                       |
                             +---------v----------+
                             |                    |     Collection of wells
                             |       Site         |
                             |                    |
                             +--------------------+

### Import Overview ###


             +---------------+
             |  Bammens API  |      ~12.500 wells/containers
             +----------+----+
                        |
             +----------v----+
             |  Scrape API   |
             +-----+---------+
Feedback           |
             +-----v---------+
     <-------+  BGT merge    |       ~8500 wells merged with BGT (8-2018)
             +------+--------+
                    |
Feedback            |
             +------v--------+
     <-------+  Cleanup      |       Fills site endpoint for route planning/ dashboards
             +------+--------+
                    |
                    |
Feedback     +------v--------+
    <--------+  API / Geo    |
             +---------------+


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

### TIP ###

check the deploy import scrips.


#### Local development ####

Create a local environment and activate it:
```
virtualenv --python=$(which python3) venv
source venv/bin/activate
`

Start development database
```
docker-compose up database
```

load production data
```
docker-compose exec database update-db.sh afvalcontainers
```


pip install -r requirements.txt in the api folder and scrape_api folder.


scrape api
==========

```
	bash load_bgt.sh (replace spreeker with your user name)
```

This will load all needed BGT and WFS data source.
No you should be able to start developing.


Afvalcontainer API
==================

This is a standard Django Rest Framework API.

```
docker-compose up database
python manage.py runserver
```


cmsdownloader (old legacy)
=============
``
To run the downloader and uploader to Postgres in a docker you can use this command:
```
docker-compose build database
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
