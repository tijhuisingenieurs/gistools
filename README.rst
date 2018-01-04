gistools
===================

todo


Requirements
------------

- shapely
- rtree
- python-dateutil

Optional:
- fiona
- gdal

Installation
------------

Windows:
download for next packages the 32-bit versions for python 2.7 from http://www.lfd.uci.edu/~gohlke/pythonlibs/ :
- rtree (Rtree‑0.8.3‑cp27‑cp27m‑win32.whl)
- shapely (Shapely‑1.5.17‑cp27‑cp27m‑win32.whl)
- python-dateutil (python_dateutil‑2.6.1‑py2.py3‑none‑any.whl). Python-dateutil is included in ArcGIS python version.

optional:
- gdal (GDAL‑2.1.3‑cp27‑cp27m‑win32.whl)
- fiona (Fiona‑1.7.3‑cp27‑cp27m‑win32.whl)

install these packages with pip (for arcGIS python version this is:
C:\Python27\ArcGIS10.<X>\Scripts\pip install <location of package>


Release
-------

todo


Tests
-----

Run tests using ``nose``. Make sure ``nose`` is inatalled (``pip install nose``).
If your python installation is added to ``PATH``, go to source root and run::

    $ nosetests

If python version is not added to ``PATH`` (like QGis or arcGIS Python installations)::

    $ c:\path_to_python_version\python.exe -m nose

Add test by adding files to 'test' directory and make sure 'test' is in the filename