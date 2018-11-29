# Afvalcontainers #


## Scrape API ##

Python script to download all the containers, containertypes and wells from https://bammensservice.nl api

Swagger documentation can be found here after you login: https://bammensservice.nl/api/doc

*LIVE* data from kilogram.nl, sidcon and enevo.

### Model Overview ###

```


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
```

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

this import process dumps 1) the raw bammens data, 2) the cleaned data and the final
data with sites 3) in the object store for the past 20 days!
so you can start and debug in any step in the import process.

```
db_slurp=raw bammens data
db_dump=first imported data
db_cleaned=final cleanup data with sites
```

#### Local development ####

Create a local environment and activate it:
```
virtualenv --python=$(which python3) venv
source venv/bin/activate
```

Start development database


```
	docker-compose up database
```

load production data:


```
	docker-compose exec database update-db.sh afvalcontainers
```

```
pip install -r requirements.txt
```

The api folder and scrape_api folder both have requirements.


scrape api
==========

```
	bash load_bgt.sh (replace spreeker with your user name)
```

See README in the scrape_api folder.

This will load all needed BGT and WFS data source.
No you should be able to start developing.


Afvalcontainer API
==================

This is a standard Django Rest Framework API.

```
	docker-compose up database
	python manage.py runserver
```


