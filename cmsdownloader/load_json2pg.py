import os
import subprocess
import logging
import argparse
import configparser
import json

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

import pandas as pd
from pandas.io.json import json_normalize
#from shapely.geometry import Point
#from shapely.geometry import wkb_hex


FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


def load_containers(datadir, config_path, dbConfig):
    config = configparser.RawConfigParser()
    config.read(config_path)

    # datadir = 'data/aanvalsplan_schoon/crow'
    files = os.listdir(datadir)
    files_json = [f for f in files if f[-5:] == '.json']
    print(files_json)

    # Load all files into 1 big dataframe with lat lon as 4326
    df = pd.DataFrame()
    for fileName  in files_json:
        with open(datadir+'/'+fileName,'r') as response:
            data = json.loads(response.read())
            # Get first name to use as title of table
            objectKeyName = list(data[0].keys())[0]
            print(fileName + " object opened")
            data = [item[objectKeyName] for item in data]
            # print(data[0])
            df = json_normalize(data)
            # print(df.head())
            # Create shapely point object
            # geometry = [Point(xy) for xy in zip(df['location.position.latitude'], df['location.position.longitude'])]
            # Convert to lossless binary to load properly into Postgis
            # df['geom'] = geometry.wkb_hex
            print("DataFrame " + objectKeyName + " created")
            LOCAL_POSTGRES_URL = URL(
                drivername='postgresql',
                username=config.get(dbConfig,'user'),
                password=config.get(dbConfig,'password'),
                host=config.get(dbConfig,'host'),
                port=config.get(dbConfig,'port'),
                database=config.get(dbConfig,'dbname')
            )

            # Write our data to database
            tableName = fileName[0:-5]
            engine = create_engine(LOCAL_POSTGRES_URL)
            df.to_sql(tableName, engine, if_exists='replace') #,  dtype={geom: Geometry('POINT', srid='4326')})
            print(tableName + ' added to Postgres')


def parser():
    desc = 'Upload container jsons into PostgreSQL.'
    parser = argparse.ArgumentParser(desc)
    parser.add_argument(
        'datadir', type=str, help='Local data directory')
    parser.add_argument(
        'config_path', type=str, help='full path of config.ini including name')
    parser.add_argument(
        'dbConfig', type=str, help='database config settings: dev or docker')
    return parser


def main():    
    args = parser().parse_args()
    load_containers(args.datadir, args.config_path, args.dbConfig)


if __name__ == '__main__':
    main()
