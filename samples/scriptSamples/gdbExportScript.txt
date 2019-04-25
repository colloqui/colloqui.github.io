import subprocess
import sys
import os
import arcpy
import datetime

jobIDList = {
	#!!!RUN EACH MARKET SEPARATELY!!!
	#'JobID#1':{'customerID':'JobID1','exportType':'CPD'},
	#'JobID#2' :{'customerID':'JobID2','exportType':'AS-BUILT'},
	

	}
	
date = str(datetime.date.today().strftime('%m_%d_%Y'))
exportdate = '_' + date

def execute(command): #Points to OSGEO SHELL and executes commands in python window.
	os.chdir('C:\\OSGeo4W64\\bin')
	#subprocess.check_call(command,shell=True)
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	# Poll process for new output until finished
	while True:
		nextline = process.stdout.readline()
		if nextline == '' and process.poll() is not None:
			break
		sys.stdout.write(nextline)
		sys.stdout.flush()

	output = process.communicate()[0]
	exitCode = process.returncode
	

def ogrCommands(WO): #WORKING 02.28.2019

	#filepath = "\\\CHCCLD01SDEV02\\d$\\GIS_team\\CO\\markWorkspace\\exports\\LLD\\{}_export_{}.gdb".format(WO,date)
	filepath = "C:\\Users\\colloqui\\Desktop\\markWorkspace\\exports\\LLD\\{}_export_{}.gdb".format(WO,date)

	ogrCMDS = [
		"""ogr2ogr -f "FileGDB" "{0}" PG:"host=12.3.4.56 user=postgres port=5432 dbname=data_base password=<password>" schema.structure -lco GEOMETRY_NAME=geom -where "jobID ilike '%%{1}%%'" -nln "Structure" -skipfailures""".format(filepath,WO),
		"""ogr2ogr -update -f "FileGDB" "{0}" PG:"host=12.3.4.56 user=postgres port=5432 dbname=data_base password=<password>" schema.span -lco GEOMETRY_NAME=geom -where "jobID ilike '%%{1}%%'" -nln "span" -skipfailures""".format(filepath,WO),
		"""ogr2ogr -update -f "FileGDB" "{0}" PG:"host=12.3.4.56 user=postgres port=5432 dbname=data_base password=<password>" schema.transmedia -lco GEOMETRY_NAME=geom -where "jobID ilike '%%{1}%%'" -nln "transmedia" -skipfailures""".format(filepath,WO),
		"""ogr2ogr -update -f "FileGDB" "{0}" PG:"host=12.3.4.56 user=postgres port=5432 dbname=data_base password=<password>" schema.attachment -lco GEOMETRY_NAME=geom -where "jobID ilike '%%{1}%%'" -nln "attachment" -skipfailures""".format(filepath,WO),
		"""ogr2ogr -update -f "FileGDB" "{0}" PG:"host=12.3.4.56 user=postgres port=5432 dbname=data_base password=<password>" schema.spliceclosure -lco GEOMETRY_NAME=geom -where "jobID ilike '%%{1}%%'" -nln "spliceclosure" -skipfailures""".format(filepath,WO),
		"""ogr2ogr -update -f "FileGDB" "{0}" PG:"host=12.3.4.56 user=postgres port=5432 dbname=data_base password=<password>" schema.buildingfootprint -lco GEOMETRY_NAME=geom -where "jobID ilike '%%{1}%%'" -nln "buildingfootprint" -skipfailures""".format(filepath,WO),
		"""ogr2ogr -update -f "FileGDB" "{0}" PG:"host=12.3.4.56 user=postgres port=5432 dbname=data_base password=<password>" schema.equipment -lco GEOMETRY_NAME=geom -where "jobID ilike '%%{1}%%'" -nln "equipment" -skipfailures""".format(filepath,WO),
		"""ogr2ogr -update -f "FileGDB" "{0}" PG:"host=12.3.4.56 user=postgres port=5432 dbname=data_base password=<password>" schema.fibersplice -where "jobID ilike '%%{1}%%'" -nln "fibersplice" -skipfailures""".format(filepath,WO),
		"""ogr2ogr -update -f "FileGDB" "{0}" PG:"host=12.3.4.56 user=postgres port=5432 dbname=data_base password=<password>" schema.optrptrport -where "jobID ilike '%%{1}%%'" -nln "optrptrport" -skipfailures""".format(filepath,WO),
		"""ogr2ogr -update -f "FileGDB" "{0}" PG:"host=12.3.4.56 user=postgres port=5432 dbname=data_base password=<password>" -sql "select s.jobID,s.fqn_id as SPAN_FQN_ID, t.fqn_id as TRANSMEDIA_FQN_ID,t.jobID from (select jobID, fqn_id, wkb_geometry from schema.transmedia where jobID = '{1}') t left join (select jobID, fqn_id, wkb_geometry from schema.span where jobID = '{1}') s on st_intersects(t.wkb_geometry,st_buffer(st_line_interpolate_point(st_linemerge(s.wkb_geometry),.5),.000001)) union select s.jobID,s.fqn_id as SPAN_FQN_ID, t.fqn_id as TRANSMEDIA_FQN_ID,t.jobID from (select jobID, fqn_id, wkb_geometry from schema.transmedia where jobID = '{1}') t right join (select jobID, fqn_id, wkb_geometry from schema.span where jobID = '{1}') s on st_intersects(t.wkb_geometry,st_buffer(st_line_interpolate_point(st_linemerge(s.wkb_geometry),.5),.000001));" -nln "Transmedia_Span_Association" -skipfailures""".format(filepath,WO),
		]

	for cmd in ogrCMDS:
		print "Executing command:\n"+cmd
		execute(cmd) # executes the above commands.
		
def woHierControlFile(file):
	
	with open(file,"w") as f:
		f.write(""""market":"<CITY NAME>"
"vendorEmailIds":"cdolloqui@gmail.com"
"mileStoneUpdates":"Y"
"woName":""
"buildStage":""
"designType":""
"woOverwrite":""
""")
		
def gdbControlFile(WO,file,customerID,export):
	
	if jobIDList[WO]['market'] == '<CITY ABREVIATION>':
		with open(file, "w") as f:
			f.write(""""market":"<CITY NAME>"
"vendorEmailIds":"cdolloqui@gmail.com"
"mileStoneUpdates":"N"
"woName":"{}"
"buildStage":"{}"
"designType":"Core"
"woOverwrite":"N"
""".format(customerID,export))

	elif jobIDList[WO]['market'] == '<CITY ABREVIATION>':
		with open(file, "w") as f:
			f.write(""""market":"<CITY NAME>"
"vendorEmailIds":"cdolloqui@gmail.com"
"mileStoneUpdates":"N"
"woName":"{}"
"buildStage":"{}"
"designType":"Core"
"woOverwrite":"N"
""".format(customerID,export))


def gdbExport():
	
	#CREATES DELIVERABLE FOLDER FOR EACH DATE. CATEGORIZE BY LLD OR ASBUILT
	mark1_folderPath = os.path.join("C://Users/colloqui/Path/to/folder", date)
	mark1_pathExists = os.path.exists(mark1_folderPath)
	mark2_folderPath = os.path.join("C://Users/colloqui/path/to/folder", date)
	mark2_pathExists = os.path.exists(mark2_folderPath)
	
	#Check if folder path exists for mark1 and create if false.
	if mark1_pathExists is False:
		print "Folder Path for mark1 does not exist.	Creating folder path:\n" + mark1_folderPath + "\n With today's date: " + date
		os.makedirs(mark1_folderPath)
	else:
		print "Folder path exists: " + date
	
	#Check if folder path exists for mark2 and create if false.
	if mark2_pathExists is False:
		print "Folder Path for mark2 does not exist.	Creating folder path:\n" + mark2_folderPath + "\n With today's date: " + date
		os.makedirs(mark2_folderPath)
	else:
		print "Folder path exists: " + date
	
	#Runs ogr2ogr commands to export features from CGIS
	for WO in jobIDList:
		print "Running ogr2ogr for " + WO
		ogrCommands(WO)
		
	# delete old scratch gdb
	if arcpy.Exists("C:/Users/colloqui/Desktop/markWorkspace/python/test" + ".gdb"):
		print "\ntest.gdb exists and is being replaced...\n"
		arcpy.Delete_management("C:/Users/colloqui/Desktop/markWorkspace/python/test" + ".gdb")

	#Creates new scratch GDB
	arcpy.CreateFileGDB_management("C:/Users/colloqui/Desktop/markWorkspace/python", "test.gdb")
	
	#Begins Work Order GDB export
	for WO in jobIDList:

		jobID2 = jobIDList[WO]['customerID'] 
		jobIdExpType = jobIDList[WO]['exportType']
		
		print("\nStarting export for " + WO)
		
		

		#copy template GDB with jobID name
		print "Copying template GDB with job ID name...\n"
		arcpy.env.workspace = "C:/Users/colloqui/Desktop/markWorkspace"
		arcpy.Copy_management("C:/Users/colloqui/Desktop/markWorkspace/templates/template.gdb", "C:/Users/colloqui/Desktop/markWorkspace/deliverables/LLD/" + os.sep + jobID2 + ".gdb")

		table = "C:/Users/colloqui/Desktop/markWorkspace/exports/LLD/" + WO + "_export" + exportdate

		#replace jobID value with jobID2 value
		print "Replacing work order ID values...\n"
		arcpy.CalculateField_management(in_table= table + ".gdb/Attachment",field="JOBID",expression="'{}'".format(jobID2),expression_type="PYTHON_9.3",code_block="#")
		arcpy.CalculateField_management(in_table= table + ".gdb/BuildingFootprint",field="JOBID",expression="'{}'".format(jobID2),expression_type="PYTHON_9.3",code_block="#")
		arcpy.CalculateField_management(in_table= table + ".gdb/Equipment",field="JOBID",expression="'{}'".format(jobID2),expression_type="PYTHON_9.3",code_block="#")
		arcpy.CalculateField_management(in_table= table + ".gdb/Span",field="JOBID",expression="'{}'".format(jobID2),expression_type="PYTHON_9.3",code_block="#")
		arcpy.CalculateField_management(in_table= table + ".gdb/SpliceClosure",field="JOBID",expression="'{}'".format(jobID2),expression_type="PYTHON_9.3",code_block="#")
		arcpy.CalculateField_management(in_table= table + ".gdb/Structure",field="JOBID",expression="'{}'".format(jobID2),expression_type="PYTHON_9.3",code_block="#")
		arcpy.CalculateField_management(in_table= table + ".gdb/Transmedia",field="JOBID",expression="'{}'".format(jobID2),expression_type="PYTHON_9.3",code_block="#")
		arcpy.CalculateField_management(in_table= table + ".gdb/FIBERSPLICE",field="JOBID",expression="'{}'".format(jobID2),expression_type="PYTHON_9.3",code_block="#")
		arcpy.CalculateField_management(in_table= table + ".gdb/OptRptrPort",field="JOBID",expression="'{}'".format(jobID2),expression_type="PYTHON_9.3",code_block="#")
		arcpy.CalculateField_management(in_table= table + ".gdb/Transmedia_Span_Association",field="JOBID",expression="'{}'".format(jobID2),expression_type="PYTHON_9.3",code_block="#")



		#copy features from export to template
		print ("Copying features from export to template...\n")
		arcpy.Append_management(inputs= table + ".gdb/Attachment", target="C:/Users/colloqui/Desktop/markWorkspace/deliverables/LLD" + os.sep + jobID2 + ".gdb" + os.sep + "TelecomDataset/Attachment", schema_type="NO_TEST", field_mapping="", subtype="")
		arcpy.Append_management(inputs= table + ".gdb/BuildingFootprint", target="C:/Users/colloqui/Desktop/markWorkspace/deliverables/LLD" + os.sep + jobID2 + ".gdb" + os.sep + "TelecomDataset/BuildingFootPrint", schema_type="NO_TEST", field_mapping="", subtype="")
		arcpy.Append_management(inputs= table + ".gdb/Equipment", target="C:/Users/colloqui/Desktop/markWorkspace/deliverables/LLD" + os.sep + jobID2 + ".gdb" + os.sep + "TelecomDataset/Equipment", schema_type="NO_TEST", field_mapping="", subtype="")
		arcpy.Append_management(inputs= table + ".gdb/Span", target="C:/Users/colloqui/Desktop/markWorkspace/deliverables/LLD" + os.sep + jobID2 + ".gdb" + os.sep + "TelecomDataset/Span", schema_type="NO_TEST", field_mapping="", subtype="")
		arcpy.Append_management(inputs= table + ".gdb/SpliceClosure", target="C:/Users/colloqui/Desktop/markWorkspace/deliverables/LLD" + os.sep + jobID2 + ".gdb" + os.sep + "TelecomDataset/SpliceClosure", schema_type="NO_TEST", field_mapping="", subtype="")
		arcpy.Append_management(inputs= table + ".gdb/Structure", target="C:/Users/colloqui/Desktop/markWorkspace/deliverables/LLD" + os.sep + jobID2 + ".gdb" + os.sep + "TelecomDataset/Structure", schema_type="NO_TEST", field_mapping="", subtype="")
		arcpy.Append_management(inputs= table + ".gdb/Transmedia", target="C:/Users/colloqui/Desktop/markWorkspace/deliverables/LLD" + os.sep + jobID2 + ".gdb" + os.sep + "TelecomDataset/Transmedia", schema_type="NO_TEST", field_mapping="", subtype="")
		arcpy.Append_management(inputs= table + ".gdb/FIBERSPLICE", target="C:/Users/colloqui/Desktop/markWorkspace/deliverables/LLD" + os.sep + jobID2 + ".gdb" + os.sep + "FIBERSPLICE", schema_type="NO_TEST", field_mapping="", subtype="")
		arcpy.Append_management(inputs= table + ".gdb/OptRptrPort", target="C:/Users/colloqui/Desktop/markWorkspace/deliverables/LLD" + os.sep + jobID2 + ".gdb" + os.sep + "OptRptrPort", schema_type="NO_TEST", field_mapping="", subtype="")
		arcpy.Append_management(inputs= table + ".gdb/Transmedia_Span_Association", target="C:/Users/colloqui/Desktop/markWorkspace/deliverables/LLD" + os.sep + jobID2 + ".gdb" + os.sep + "Transmedia_Span_Association", schema_type="NO_TEST", field_mapping="", subtype="")
		
		print("***GDB Export for " + WO + " complete***")
		
		print("Creating Control file for " + WO)
		
		if jobIDList[WO]['market'] == 'mark1':
			ctrlFile = os.path.join(mark1_folderPath, jobID2 + ".gdb.txt")
			gdbControlFile(WO,ctrlFile,jobID2,jobIdExpType)		
		elif jobIDList[WO]['market'] == 'mark2':
			ctrlFile = os.path.join(mark2_folderPath, jobID2 + ".gdb.txt")
			gdbControlFile(WO,ctrlFile,jobID2,jobIdExpType)
			
	print("\n***GDB exports completed***\n")
	#EVERYTHING BEFORE THIS LINE WORKS-------------------------------------------

	
	
def job_hier_create():	
	
	for WO in jobIDList:
		if WO == list(jobIDList)[0]:
			query = "a.internal_job_id ILIKE '%{}%' and isdeleted = 'f'".format(list(jobIDList)[0])
			
		else:
			query += " or a.internal_job_id ILIKE '%{}%' and isdeleted = 'f' ".format(WO)
			
	

	if arcpy.Exists(r"C:\Users\colloqui\Desktop\markWorkspace\deliverables\LLD\JOB_HIERARCHY.gdb"):
		print "JOB_HIERARCHY.gdb LIVES!"
	else:
		arcpy.Copy_management("C:/Users/colloqui/Desktop/markWorkspace/templates/JOB_HIERARCHY.gdb", "C:/Users/colloqui/Desktop/markWorkspace/deliverables/LLD/JOB_HIERARCHY.gdb")

		targetGDB = "C:/Users/colloqui/Desktop/markWorkspace/deliverables/LLD/JOB_HIERARCHY.gdb"
		
		
		f2fOGR = """ogr2ogr -update -append -f "FileGDB" "{}" PG:"host=12.3.4.56 user=postgres port=5432 dbname=data_base password=<password>" -sql "sql query to reference customer job IDs" -nln "JOB_HIERARCHY" -skipfailures""".format(targetGDB,query)
		
		print "running ogr2ogr for JOB_HIERARCHY...\n" + f2fOGR
		execute(f2fOGR)
		
		
		print("***JOB HIERARCHY GDB created***")
		#write Control File
		print("Writing JOB HIERARCHY control file...")
		jobHierFile = 'C:/Users/colloqui/Desktop/markWorkspace/deliverables/LLD/JOB_HIERARCHY.gdb.txt'
		woHierControlFile(jobHierFile)


	
def main():
	gdbExport()
	job_hier_create()

if __name__ == '__main__':
	main()
