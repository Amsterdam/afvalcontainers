# CMS Downloader #

Python script to download all the containers, containertypes and wells from https://bammensservice.nl api into seperate jsons.
Swagger can be found here after you login: https://bammensservice.nl/api/doc
The results can be found here as an example: https://github.com/Amsterdam/schoonmonitor/tree/master/cmsdownloader/data.

### Install procedure ###

```
git clone https://github.com/Amsterdam/afvalcontainers.git afvalcontainers
cd afvalcontainers
```

Create a local environment and activate it:
```
virtualenv --python=$(which python3) venv
source venv/bin/activate
```

Install the packages 
```
cd cmsdownloader
pip install -r requirements.txt
```

Before you can use the api you must add the login ENV variables
```
export CKAN_API=****
export BAMMENS_API_USERNAME=****
export BAMMENS_API_PASSWORD=****
```
To run the downloader and uploader to Postgres in a docker you can use this command:
```
docker-compose build cmsdownloader
docker-compose up cmsdownloader
```

To run the downloader locally with stating the folder and where to write to.
```
sh ./cmsdownloader/docker_run.sh
```
Run the uploader to postgres locally with stating the folder and postgres login and port where to write to.
```
docker-compose build database
docker-compose up database
python cmsdownloader.py data dev
```
