import json
import csv
import os.path

from collection import MemCollection, OrderedDict

import logging
log = logging.getLogger(__name__)


def export_memcollection_to_csv(point_col, csv_name):
    """ export content of point collection with appropriate attributes to 
    a csv file with measurement points and attributes
    
    receives collection of points with attributes
    
    and file location + name for metingen
    
    returns csv file"""

    with open(csv_name, 'wb') as csvfile:

        fieldnames = next(point_col.filter())['properties'].keys()    
        

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';',
                                quoting=csv.QUOTE_NONE,
                                quotechar='', escapechar='\\')
        
        # wegschrijven data
        writer.writeheader()
                
        for row in point_col:
            regel = {}
            for field in fieldnames:
                regel[field] = row['properties'].get(field, '')
            writer.writerow(regel)
    
    return
    