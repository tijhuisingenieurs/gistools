@echo off
: set OSGEO4W root to match own installation
SET OSGEO4W_ROOT=C:\OSGeo4W64
call "%OSGEO4W_ROOT%"\bin\o4w_env.bat
call "%OSGEO4W_ROOT%"\apps\grass\grass-7.2.0\etc\env.bat

set PATH=%PATH%;%OSGEO4W_ROOT%\apps\qgis\bin
set PATH=%PATH%;%OSGEO4W_ROOT%\bin

set PYTHONPATH=%PYTHONPATH%;%USERPROFILE%\.qgis2\python\plugins\
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\Python27\Lib\site-packages
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT%\apps\qgis

: set link to Liclips executable
start "Liclips aware of QGIS" /B "C:\Program Files\Brainwy\LiClipse 3.4.0\LiClipse.exe"
PAUSE