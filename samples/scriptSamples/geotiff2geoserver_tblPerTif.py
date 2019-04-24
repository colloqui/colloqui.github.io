#This script pulls geotiffs from a folder with the day's date.
#The geotiffs are uploaded to PostGIS tables using their assigned SRID #'s.
#Geoserver processes the PostGIS tables 

import os
import sys
import datetime
from osgeo import gdal
import osr
import psycopg2
import subprocess
import textwrap
import requests

#Variables for raster2pgsql command. Update accordingly.
dbName = 'raster'
dbHost = '10.1.5.23' #DEV
dbUser = 'postgres'
dbPW = 'chcGIS01!02#'
dbPort = '5432'
schema = 'public'

time = str(datetime.datetime.now().time())
date = str(datetime.date.today()).replace("-","")
yesterday = str(datetime.date.today()-datetime.timedelta(days=1)).replace("-","") #may need if running script after midnight. The congruex folder will have the previous date if after midnight.

cngrxPath = 'C:\Users\colloqui\Congruex\GIS-Team - CCLD GeoTIFF\Active GeoTIFF\\' + date 
logPath = r"C:\Users\colloqui\Desktop\TESTgeotiffs\logs\rasterLog.txt"

#Need geotiff checks and standardization


#Creates XML config files for each geotiff uploaded.
def createXML(covName): 
	xmlPath = r"\\chcorg01pgis01\D$\webgis\data_geoserver\coverages\{}.pgraster.xml".format(covName)
	xml_exist = os.path.isfile(xmlPath)
	print "XML file exists: " + str(xml_exist)
	if xml_exist is False:
		print "Creating configuration file: {}.pgraster.xml".format(covName)
		with open(xmlPath,"w") as newXML:
			newXML.write(textwrap.dedent(
				"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
				<!DOCTYPE ImageMosaicJDBCConfig [
					<!ENTITY mapping PUBLIC "mapping"	 "mapping.pgraster.xml.inc">
					<!ENTITY connect PUBLIC "connect"	 "connect.pgraster.xml.inc">
				]>

				<config version="1.0">
					<coverageName name="{}"/>
					<coordsys name="EPSG:4326"/>
					<!-- interpolation 1 = nearest neighbour, 2 = bipolar, 3 = bicubic -->
					<scaleop	interpolation="1"/>
					<axisOrder ignore="false"/>
					&mapping;
					&connect;
				</config>
				""".format(covName)))

	
def tableExists(x):	 #This function checks for preexisting SRID Tables.
		
		exists = None
		conn = None
		
		try:
			table_str = x
			conn = psycopg2.connect(dbname=dbName,user=dbUser,password=dbPW,host=dbHost,port=dbPort)
			cur = conn.cursor()
			cur.execute("SELECT EXISTS(select relname from pg_class where relname = '" + table_str + "');")
			exists = cur.fetchone()[0]
			print str(exists) +"\t"+ table_str
			cur.close()
		except psycopg2.Error as e:
			print e
		
		return exists
		
def createCoverageStore(sridTable):
	
	url = 'http://cgisdev.chcconsulting.com:8087/geoserver/rest/workspaces/designtool_crowncastle_nw/coveragestores'
	headers = {'Content-Type':'application/xml'}
	auth = ('admin','chcGIS01!02#')
	#NEED GET list for all workspaces. This will need to add the coverage stores to every layer group involved.
	# define your XML string that you want to send to the server
	data = textwrap.dedent(
	"""<coverageStore>
	<name>{0}</name>
	<type>ImageMosaicJDBC</type>
	<enabled>true</enabled>
	<workspace>
	<name>designtool_crowncastle_nw</name>
	<atom:link xmlns:atom="http://www.w3.org/2005/Atom" rel="alternate" href="http://cgisdev.chcconsulting.com:8087/geoserver/rest/workspaces/designtool_crowncastle_nw.xml" type="application/xml"/>
	</workspace>
	<__default>false</__default>
	<url>file:coverages/{0}.pgraster.xml</url>
	<coverages>
	<atom:link xmlns:atom="http://www.w3.org/2005/Atom" rel="alternate" href="http://cgisdev.chcconsulting.com:8087/geoserver/rest/workspaces/designtool_crowncastle_nw/coveragestores/{0}/coverages.xml" type="application/xml"/>
	</coverages>
	</coverageStore>
	""".format(sridTable))
	
	#fire the request
	r = requests.post(url,headers=headers,auth=auth,data=data)
	
	#inspect the response
	print "Inspecting response from geoserver store creation..."
	print(r.text)

def reproject(inFile,epsg,outFile): #If the file is not 4326, it will be reprojected as such.
	#warpCMD = 'gdalwarp -s_srs EPSG:{} -t_srs EPSG:4326 "{}" "{}"'.format(epsg,inFile,targetFile) #NOT GONNA WORK!
	gdal.Warp(outFile, inFile, dstSRS='EPSG:4326')
	print "Reprojecting " + file
	#os.chdir('C:\Program Files\PostgreSQL\9.6\\bin') #Fixes python version error
	#subprocess.check_call(warpCMD,shell=True) #WAITs UNTIL FINISHED.
	return outFile

def ImageMosaic():
	for path, dirs, files in os.walk(cngrxPath):
		for f in files:
			if not f.endswith(".tif"):
				continue
			
			epsg = "4326"
			outFile = "warped_" + f
			reproject(f,epsg, outFile)
	
def geotiff2db():  #Uploads geotiffs to the postgres database
		
		print "--------------------------------PYTHON BEGIN---------------------------------"
		print "Began running NEW geotiff2geoserver (02/19/2019) at: " + time + " on " + str(datetime.date.today())
		
		if not os.path.exists(cngrxPath): #if cngrxPath does not exist, stop script
				print "\nERROR: Folder " + date + " does not exist in cngrxPath"
				
		for path, dirs, files in os.walk(cngrxPath): #iterate through sharepoint folder.
				for f in files:
						tableName = (os.path.splitext(f)[0])[:10] + "_" + date #+ count
						#Check for file extension .tif
						if not f.endswith(".tif"):
								continue
						
						#Get srid number from geotiff and insert into cmd
						path = cngrxPath +"\\"+ f
						d = gdal.Open(path)
						proj = osr.SpatialReference(wkt=d.GetProjection())
						epsg = str(proj.GetAttrValue('AUTHORITY',1))
						srid_table = tableName + '_4326'
						reprojFile = f
						
						#NEEDS FOOL PROOF NAMING CONVENTION!!!!!!!!!!!
						
						print("\nThe ESPG for " + f + " is: " + epsg + "\nAnd the srid_table is: " + srid_table)
						if epsg != "4326":
							print "Don't worry, we're changing it to 4326!"
							t_file = f.replace(".","_reproj.")
							reprojFile = reproject(f,epsg,t_file)
							return reprojFile
							#WILL NEED TO REASIGN THE FILE IF A COPY IS MADE
						else:
							print "The ESPG is 4326 and will stay that way!"
						
						#Enters postgis DB password
						os.environ['PGPASSWORD'] = dbPW 
						       
						#Checks for preexisting table and either creates the table or appends to the existing.
						if tableExists(srid_table) == False:
							cmd = 'raster2pgsql -I -Y -M -s 4326 -l 2,4,8,16,32,64 "{}\{}" -t 256x256 {}.{} | psql -h {} -U {} -p {} -d {} > {} 2>&1'.format(
										cngrxPath,reprojFile,schema,srid_table,dbHost, dbUser, dbPort, dbName,logPath)
							print "Creating postgis table called: " + srid_table
							os.chdir('C:\Program Files\PostgreSQL\9.6\\bin') #Fixes python version error
							subprocess.check_call(cmd,shell=True) #WAITs UNTIL FINISHED.
							
							#xml File creation
							covName = "ccld_imagery_4326"
							xmlPath = r"\\chcorg01pgis01\D$\webgis\data_geoserver\coverages\{}.pgraster.xml".format(covName)
							xmlExists = os.path.isfile(xmlPath)
							#if xml file already exists, skip.
							if not xmlExists:
								continue
							else:
								createXML(covName)
							
							#Update mosaic table  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
							mosaic_insert_cmd = "INSERT INTO {}.mosaic (tiletable) SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_catalog = 'raster' AND table_schema = 'public' AND table_name <> 'mosaic' AND table_name <> 'spatial_ref_sys' AND table_name ILIKE '%{}%';".format(schema,srid_table)

							mosaic_update_cmd = "UPDATE {}.mosaic SET name = '{}' where tiletable ILIKE '%{}%'".format(schema,covName,srid_table)
							
							#possibly need a SQL statement for constraints. this will replace the -C in the raster2pgsql.
							#the resolution constraint may not allow for multiple geotiffs to be uploaded to postgis
							
							print("Connecting to " + dbHost)
							conn = psycopg2.connect(dbname=dbName,user=dbUser,password=dbPW,host=dbHost,port=dbPort)
							cur = conn.cursor()
							print("Executing mosaic table insert statement:\n" + mosaic_insert_cmd)
							cur.execute(mosaic_insert_cmd)
							conn.commit()
							print("Executing mosaic table update statement:\n" + mosaic_update_cmd)
							cur.execute(mosaic_update_cmd)
							print "Committing changes!"
							conn.commit()
							print("Closing connection to " + dbHost)
							conn.close()
							
							#Creates Coverage Store in geoserver with the name of the srid table.  Still NEEDS layer publishing.
							#createCoverageStore(covName)
							#print "Created Geoserver (" + dbHost + ") coverage store: " + covName
							
						#tableExists can be assigned to a variable 
						elif tableExists(srid_table) == True:
							cmd = 'raster2pgsql -a -I -Y -M -s 4326 -l 2,4,8,16,32,64 "{}\{}" -t 256x256 {}.{} | psql -h {} -U {} -p {} -d {} > {} 2>&1'.format(
									   epsg,cngrxPath,f,schema,srid_table,dbHost, dbUser, dbPort, dbName,logPath)
							print("Appending table: " + srid_table)
							os.chdir('C:\Program Files\PostgreSQL\9.6\\bin') #Fixes python version error
							subprocess.check_call(cmd,shell=True) #WAITs UNTIL FINISHED.
							
							#NEEDS ERROR HANDLING
						
						
						#LOG FUNCTION NEEDED
						#number of pyramids = log(pixelsize of image) / log(2) - log (pixelsize of tile) / log(2).
						#storey lane is:  log(57089)/log(2)-log(256)/log(2) = 7.8 = 7 pyramids
						#64th is: log(36318)/log(2)-log(256)/log(2) = 7.14 = 7 pyramids
						#54th is: log(37461)/log(2)-log(256)/log(2) = 7.19 = 7 pyramids
						#Log Function below
						#int(math.floor(math.log(57089)/math.log(2)-math.log(256)/math.log(2)))
						
						
						
						print "\nNEXT geotiff file..."

		print "\n------------------------------------PYTHON END----------------------------------"								
		

def main():
	#print tableExists("raster") #This is the counter for multiple tables
	#geotiff2db()
	ImageMosaic()
	#tableExists('srid_6465')
	#print tableExists('srid_6465')
if __name__ == '__main__':
	main()
