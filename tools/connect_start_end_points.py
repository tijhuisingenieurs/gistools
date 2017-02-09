from utils.collection import TCollection



def connect_start_endpoints():

    filename = 'c:/tmp/test.shp'

    lines = TCollection(filename)

    points = TCollection()
    connecting_lines = TCollection()

    for feature in lines.features:
        for point in (feature['geometry']['coordinates'][0],
                      feature['geometry']['coordinates'][-1]):

            points.add({'geometry':{'type': 'Point', 'coordinates': point},
                        'properties': {'line_id': feature['id']}})

    for point in points:
        if not point['properties']['matched']:
            point_polygon = todo
            points.getfeatures(within=point_polygon)




