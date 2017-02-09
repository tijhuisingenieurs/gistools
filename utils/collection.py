import fiona


class Collection(object):

    def __init__(self, filename=None):
        self.filename = filename
        self.source = None

    def _open(self):

        if self.source is None:
            self.source = fiona.open(self.filename, 'r')

    def copy_collection_to_new_file(self):
        pass

    @property
    def features(self):
        """ iterator over features of collection"""
        self._open()

        for feature in self.source:
            # do something
            yield feature
