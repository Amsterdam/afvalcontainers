import json


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
        print(item)
        item = flatten_json(item)
        print(item)
        if lonColumn:
            feature = {'type': 'Feature',
                       'properties': item}
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
        #objectKeyName = str(objectKeyName, 'utf-8')
        print(fileName + " object opened")
        data = [item[objectKeyName] for item in data]
        #print(data[0])
    return data


def joinByKeyNames(geojson, dataset, key1, key2):
    """Insert data from dataset to a geojson where key1 from dataset matches key2 in the geojson."""
    n = 1
    for feature in geojson['features']:
        matches = [item for item in dataset
                   if item[key1] == feature["properties"].get(key2)]
        if matches:
            feature['properties'].update(matches[0])
        else:
            feature['properties']['container'] = None
        n += 1
        print("{} of {}".format(n, len(geojson['features'])))
    return geojson


def main():
    # Prepare values for functions
    fileName = 'data/wells.json'
    fileName2 = 'data/containers.json'
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

    with open('data/afvalcontainers.geojson', 'w') as outFile:
        wells = openJsonArrayKeyDict2FlattenedJson(fileName)
        containers = openJsonArrayKeyDict2FlattenedJson(fileName2)
        # Build Geojson from wells
        geojson = jsonPoints2geojson(wells, lat, lon)
        # Add containers to wells
        joinByKeyNames(geojson, containers, 'id', 'containers.0')
        # Add descriptions to containers
        joinByKeyNames(geojson, waste_descriptions, 'id', 'waste_type')
        json.dump(geojson, outFile, indent=2)
        print ('written geojson')


if __name__ == '__main__':
    desc = 'convert and merge jsons to geojson'
    main()