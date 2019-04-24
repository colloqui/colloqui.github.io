@ECHO ON
REM Runs Geotiff to Geoserver python script
call "C:\Program Files (x86)\QGIS 2.18\bin\o4w_env.bat"
"C:\Program Files (x86)\QGIS 2.18\bin\python.exe" "\\CHCCLD01SDEV02\d$\GIS_team\CO\GIS-517 GEOTIFF PROJECT\geotiff2geoserver_tblPerTif.py"
ECHO Ran Geotiff to Geoserver Script

PAUSE