import sys
from fiona import Collection
from rtree import index
from shapely.geometry import shape

# use fiona collection for 'normal'use


class TCollection(list):
    """class for a temporary file"""

    def __init__(self, geometry_type='Point'):
        self.geometry_type = geometry_type
        self._spatial_index = index.Index()

    @property
    def schema(self):

        pass

    @property
    def meta(self):
        pass

    def filter(self, *args, **kwds):
        """Returns an iterator over records, but filtered by a test for
        spatial intersection with the provided ``bbox``, a (minx, miny,
        maxx, maxy) tuple or a geometry ``mask``.

        Positional arguments ``stop`` or ``start, stop[, step]`` allows
        iteration to skip over items or stop at a specific item.
        """

        start = args.get('start', 0)
        stop = min(args.get('stop', sys.maxint), len(self))
        step = args.get('step', 1)

        slice_index = range(start, stop, step)

        bbox = kwds.get('bbox')
        mask = kwds.get('mask')

        if bbox:
            bbox_index = self._spatial_index.intersection(bbox)

        # todo: hier verder


    def items(self, *args, **kwds):
        """Returns an iterator over FID, record pairs, optionally
        filtered by a test for spatial intersection with the provided
        ``bbox``, a (minx, miny, maxx, maxy) tuple or a geometry
        ``mask``.

        Positional arguments ``stop`` or ``start, stop[, step]`` allows
        iteration to skip over items or stop at a specific item.
        """
        pass

    def keys(self, *args, **kwds):
        """Returns an iterator over FIDs, optionally
        filtered by a test for spatial intersection with the provided
        ``bbox``, a (minx, miny, maxx, maxy) tuple or a geometry
        ``mask``.

        Positional arguments ``stop`` or ``start, stop[, step]`` allows
        iteration to skip over items or stop at a specific item.
        """
        pass

    @property
    def bounds(self):
        """Returns (minx, miny, maxx, maxy)."""
        return self._spatial_index.bounds

    def writerecords(self, records):
        """Stages multiple records."""

        # todo: check fields and append dynamicaly

        for record in records:
            # todo, do something with the id
            pnt = shape(record['geometry'])
            i = 0
            self._spatial_index.insert(i, pnt.bounds)

        self.extend(records)

    def write(self, record):
        """Stages a record."""
        self.writerecords([record])
