try:
    # First import qgis to set correct API versions of QString, etc.
    import qgis   # pylint: disable=W0611  # NOQA
except ImportError:
    pass

from PyQt4 import QtCore
from PyQt4 import QtGui
from qgis.gui import *
from qgis.core import *
