from rtree import index
from shapely.geometry import shape


from collections import OrderedDict

# use fiona collection for 'normal' use


class MemCollection(object):
    """Collection with same functions as fiona.collection, but which can be created in memory. Uses
        rtree to speedup spatial filtering"""

    def __init__(self, geometry_type='Point'):
        self.geometry_type = geometry_type
        self._spatial_index = index.Index()

        self.ordered_dict = OrderedDict()

    @property
    def schema(self):
        # todo
        return

    @property
    def meta(self):
        # todo
        return

    def filter(self, *args, **kwds):
        """Returns an iterator over records, but filtered by a test for
        spatial intersection with the provided ``bbox``, a (minx, miny,
        maxx, maxy) tuple or a geometry ``mask``.

        Positional arguments ``stop`` or ``start, stop[, step]`` allows
        iteration to skip over items or stop at a specific item.
        """
        selected = self.keys(*args, **kwds)

        for i in selected:
            if i in self.ordered_dict:
                yield self.ordered_dict[i]

    def items(self, *args, **kwds):
        """Returns an iterator over FID, record pairs, optionally
        filtered by a test for spatial intersection with the provided
        ``bbox``, a (minx, miny, maxx, maxy) tuple or a geometry
        ``mask``.

        Positional arguments ``stop`` or ``start, stop[, step]`` allows
        iteration to skip over items or stop at a specific item.
        """
        selected = self.keys(*args, **kwds)

        for i in selected:
            if i in self.ordered_dict:
                yield (i, self.ordered_dict[i])

    def keys(self, start=0, stop=None, step=1, **kwds):
        """Returns an iterator over FIDs, optionally
        filtered by a test for spatial intersection with the provided
        ``bbox``, a (minx, miny, maxx, maxy) tuple or a geometry
        ``mask``.

        Positional arguments ``stop`` or ``start, stop[, step]`` allows
        iteration to skip over items or stop at a specific item.
        """
        selected = set(self.ordered_dict.keys())

        # warning: this is not supported by Fiona
        if len(selected) == 0:
            return selected

        if stop is None:
            stop = max(selected) + 1
        elif stop < 0:
            stop = max(0, max(selected) + stop + 1)

        if start is None:
            start = min(selected)
        elif start < 0:
            start = max(0, max(selected) + start + 1)

        selected.intersection_update(set(range(start, stop, step)))

        bbox = kwds.get('bbox')
        mask = kwds.get('mask')

        if bbox is not None:
            selected.intersection_update(set(self._spatial_index.intersection(bbox)))

        if mask:
            # todo
            pass

        return selected

    @property
    def bounds(self):
        """Returns (minx, miny, maxx, maxy)."""
        return self._spatial_index.bounds

    def writerecords(self, records):
        """Stages multiple records."""

        if type(records) != list:
            raise ValueError('list expected, got {0}'.format(type(records)))
        if len(self) == 0:
            nr = 0
        else:
            nr = next(reversed(self.ordered_dict)) + 1

        for record in records:
            record['id'] = nr
            self.ordered_dict[nr] = record
            pnt = shape(record['geometry'])
            self._spatial_index.insert(nr, pnt.bounds)
            nr += 1

    def write(self, record):
        """Stages a record."""
        self.writerecords([record])

    def save(self,
             filename,
             crs=None,
             driver='ESRI Shapefile',
             schema=None):
        """

        """
        import fiona

        f = fiona.open(filename,
                       'w',
                       crs=crs,
                       driver=driver,
                       schema=schema)

        records = [feat for feat in self.filter()]
        f.writerecords(records)
        f.close()

        # todo: check fields and append field metadata dynamicaly

    def __len__(self):

        return len(self.ordered_dict)

    def __getitem__(self, key):

        return self.ordered_dict[key]

    def __iter__(self):

        return self.filter()
