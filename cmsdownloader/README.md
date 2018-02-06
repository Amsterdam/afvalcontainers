# CMS Downloader #

Python script to download all the containers, containertypes and wells from https://bammensservice.nl api into seperate jsons.
Swagger can be found here after you login: https://bammensservice.nl/api/doc
The results can be found here as an example: https://github.com/Amsterdam/schoonmonitor/tree/master/cmsdownloader/data.

### Install procedure ###

```
git clone https://github.com/Amsterdam/schoonmonitor.git schoonmonitor
cd schoonmonitor
```
Start the docker database
```
docker-compose build database
docker-compose up database
```

Create a local environment and activate it:
```
virtualenv --python=$(which python3) venv
source venv/bin/activate
```

Install the packages 
```
cd cmsdownloadcontainer
pip install -r requirements.txt
```

Before you can use the api you must create a config.ini file
```
create a config.ini file with the user and password credentials using the config.ini.example file
```
To run the downloader and uploader to Postgres in a docker you can use this command:
```
docker-compose build cmsdownloader
docker-compose up cmsdownloader
```

To run the downloader locally with stating the folder and where to write to.
```
python cmsdownloader.py data dev
```
Run the uploader to postgres locally with stating the folder and postgres login and port where to write to.
```
python cmsdownloader.py data dev
```
