import json
import argparse
import logging


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


def flatten_json(jsonObject):
    """
        Flatten nested json Object {"key": "subkey": { "subsubkey":"value" }} to ['key.subkey.subsubkey'] values
        https://towardsdatascience.com/flattening-json-objects-in-python-f5343c794b10
    """
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '.')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(jsonObject)
    return out


def jsonPoints2geojson(df, latColumn, lonColumn):
    """
       Convert JSON with lat/lon columns to geojson.
       https://gis.stackexchange.com/questions/220997/pandas-to-geojson-multiples-points-features-with-python
    """
    geojson = {'type': 'FeatureCollection', 'features': []}
    for item in df:
        # logger.info(item)
        item = flatten_json(item)
        # logger.info(item.keys())
        keep_items = {}
        for k,v in item.items():
            if k in ['id', 'id_number', 'serial_number', 'well','location.address.summary', 'location.address.district', 'location.address.neighbourhood', 'owner.name', 'created_at', 'placing_date', 'operational_date', 'warranty_date','containers.0']:
                keep_items[k] = v
        # logger.info(keep_items)
        if lonColumn:
            feature = {'type': 'Feature',
                       'properties': keep_items}
            feature['geometry'] = {'type': 'Point',
                                   'coordinates': [float(item[lonColumn]),
                                                   float(item[latColumn])
                                                   ]}
            geojson['features'].append(feature)
    return geojson


def openJsonArrayKeyDict2FlattenedJson(fileName):
    """
        Open json and return array of objects without object value name.
        For example: [{'container':{...}}, {'container':{...}}] returns now as [{...},{...}])
    """
    with open(fileName, 'r') as response:
        data = json.loads(response.read())
        objectKeyName = list(data[0].keys())[0]
        # objectKeyName = str(objectKeyName, 'utf-8')
        logger.info(fileName + " object opened")
        data = [item[objectKeyName] for item in data]
        # logger.info(data[0])
    return data


def joinByKeyNames(geojson, dataset, key1, key2):
    """Insert data from dataset to a geojson where key1 from dataset matches key2 in the geojson."""
    n = 1
    for feature in geojson['features']:
        #logger.info(feature["properties"])
        matches = [item for item in dataset
                   if item[key1] == feature["properties"].get(key2)]
        if matches:
            if  'owner' in (matches[0].keys()):
                del matches[0]['owner']
            feature['properties'].update(matches[0])
        else:
            feature['properties']['container'] = None
        n += 1
        #logger.info("{} of {}".format(n, len(geojson['features'])))
    return geojson


def parser():
    desc = "convert jsons to geojson file."
    parser = argparse.ArgumentParser(desc)
    parser.add_argument('datadir', type=str,
                        help='Local data directory.')   
    return parser

def main():
    args = parser().parse_args()
    # Prepare values for functions
    fileName = args.datadir + '/wells.json'
    fileName2 = args.datadir + '/containers.json'
    lat = 'location.position.latitude'
    lon = 'location.position.longitude'  # for use later in flattened json as item['location.position.longitude']
    waste_descriptions = [
                  {"id": 1, "waste_name": "Rest"},
                  {"id": 2, "waste_name": "Glas"},
                  {"id": 3, "waste_name": "Glas"},
                  {"id": 6, "waste_name": "Papier"},
                  {"id": 7, "waste_name": "Textiel"},
                  {"id": 9, "waste_name": "Wormen"},
                  {"id": 20, "waste_name": "Glas"},
                  {"id": 25, "waste_name": "Plastic"}]

    with open(args.datadir+'/afvalcontainers.geojson', 'w') as outFile:
        wells = openJsonArrayKeyDict2FlattenedJson(fileName)
        logger.info('Flatten wells dictionaries')
        containers = openJsonArrayKeyDict2FlattenedJson(fileName2)
        geojson = jsonPoints2geojson(wells, lat, lon)
        logger.info('Build Geojson from wells')
        joinByKeyNames(geojson, containers, 'id', 'containers.0')
        logger.info('Added containers to wells')
        joinByKeyNames(geojson, waste_descriptions, 'id', 'waste_type')
        logger.info('Added descriptions to containers')
        json.dump(geojson, outFile, indent=2)
        logger.info('Finished writing geojson')


if __name__ == '__main__':
    desc = 'convert and merge jsons to geojson'
    main()