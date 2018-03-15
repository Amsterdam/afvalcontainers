#!/usr/bin/env python
import os
import argparse
import requests
import logging
from mimetypes import MimeTypes

def logger():
    """
    Setup basic logging for console.

    Usage:
        Initialize the logger by adding the code at the top of your script:
        ``logger = logger()``

    TODO: add log file export
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S')
    logger = logging.getLogger(__name__)
    return logger


# Setup logging service
logger = logger()


def getFileType(filename_path):
    """
    Return filetype as 'type/subtype' based on extension.

    Args:
        1. filename_path: set path where file resides

    Returns:
        Returns 'type/subtype' as a string.
    """    
    mime = MimeTypes()
    content_type = mime.guess_type(filename_path)[0]
    logger.info("Found content type '{}'".format(content_type))
    return content_type


def find_resource_id_if_exists(url, dataset_name, file_name):
    metadata = requests.get(url+'/api/3/action/package_show?id='+dataset_name)
    package_metadata = metadata.json()
    for resource in package_metadata['result']['resources']:
        if resource['name'] == file_name:
            logger.info('Found existing filename: {}, wil update it now...'.format(resource['name']))
            return resource['id']


def upload_file_to_ckan(url, dataset_name, file_path):
    """
    Upload a file to the CKAN datastore.

    Args:
        1. url: url of the catalog::

            https://api.data.amsterdam.nl/catalogus

        2. dataset_name: name of the dataset, which can be found on the ckan page url::

            https://api.data.amsterdam.nl/catalogus/dataset/afvalcontainers

        3. api_key: your private user key, which can be found on the user profile page.
        4. file_path: location of the file including filename::

            /path/to/file/to/upload.csv

    Returns:
        An uploaded file to the CKAN datastore.
    """

    assert os.environ['CKAN_API_KEY']

    api_key = os.environ['CKAN_API_KEY']
    file_name = file_path.split('/')[-1]
    resource_id = find_resource_id_if_exists(url, dataset_name, file_name)

    if resource_id:
        data_upload_url = url+'/api/action/resource_update'
        data = {"id":resource_id}
    else:
        data_upload_url = url+'/api/action/resource_create'
        data={"package_id": dataset_name,
              "name":file_name,
              "description": "Generated Geojson from API from the Container Management System from Bammens.nl",
              "format":getFileType(file_name)}
        logger.info(data)     
        logger.info('Uploading {}...'.format(file_name))

    response = requests.post(data_upload_url,
                             data=data,
                             headers={"X-CKAN-API-Key": api_key},
                             files=[('upload', open(file_path, 'rb'))]
                           )
    assert response.status_code == requests.codes.ok
    logger.info('Uploaded {} to https://api.data.amsterdam.nl/catalogus/dataset/{}'.format(file_name, dataset_name))


def parser():
    """
    Parser function to run arguments from commandline and to add description to sphinx docs.
    To see possible styling options: https://pythonhosted.org/an_example_pypi_project/sphinx.html
    """
    description = """
    Upload a file to the CKAN datastore with your private user key, which can be found on the user profile page.

    Use an ENV variable to store your api key:

        ``export CKAN_API_KEY=********-****-****-****-************``

    Example command line:

        ``load_file_to_ckan https://api.data.amsterdam.nl/catalogus afvalcontainers /data/afvalcontainers.geojson``

    """

    parser = argparse.ArgumentParser(
                        description=description)
    parser.add_argument('url',
                        type=str,
                        help="""url of the catalog::

                                    https://api.data.amsterdam.nl/catalogus
                             """)
    parser.add_argument('dataset_name',
                        type=str,
                        help="""name of the dataset, which can be found on the ckan page url::

                                    https://api.data.amsterdam.nl/catalogus/dataset/afvalcontainers
                             """)
    parser.add_argument('file_path',
                        type=str,
                        help="""location of the file including filename::

                                    /path/to/file/to/upload.csv
                             """)
    return parser


def main():
    # Return all arguments in a list
    args = parser().parse_args()

    # Run all functions sequential
    upload_file_to_ckan(args.url, args.dataset_name, args.file_path)


if __name__ == "__main__":
    main()
