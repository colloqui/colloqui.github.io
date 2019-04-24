#This puts all json market keys to their own tables.

import psycopg2
import json
import requests


conn = psycopg2.connect(database = 'design_tool', user = 'postgres', host = '10.1.5.23', port = '5432')#password = 'chcGIS01!02#')
cur = conn.cursor()
json_file = ("C:\Users\colloqui\Desktop\GIS Tasks\Layer Types JSON\layerTypesJson.json")


print("Begin JSON to Table...")

def insert_values():
	with open(json_file) as f:
		data = json.load(f)
		data.keys()
		
	
	
	
	for table, field in data.iteritems():
		print "Table: " + table
		tableSel = "select * from map_services.market;"
		cur.execute(tableSel)
		
		for mv in cur.fetchall():
			muid = mv[0]
			market_value = mv[1]
			
			if market_value == table:
				print muid
				for layer, layerData in field.iteritems():
					print "	" +layer
					
					valuesDict = {"muid": muid, "market": market_value, "layer":layer}
					for column, value in layerData.iteritems():
						value = ','.join(value) if column == 'tables' else value
						
						#if column == 'editable' or column == 'ischecked':
							#value = str(value).lower()
							
						#print column + " : " + value
						
						valuesDict[column] = value
					#print valuesDict	
					
					
						#print "		" + column + " : " + str(value)
					insertCMD = "INSERT INTO map_services.layers (muid,market,layername,namefield,\"group\",editable,ischecked,type,tables) VALUES (%(muid)s,%(market)s,%(layer)s,%(nameField)s,%(group)s,%(editable)s,%(ischecked)s,%(type)s,%(tables)s)"
					mog = cur.mogrify(insertCMD,(valuesDict))
					print mog
					cur.execute(insertCMD,(valuesDict))
					
	return

def main():
	#create_table()
	insert_values()
	#print("Table Name: %s" % tablename)


if __name__ == '__main__':
	main()

conn.commit()
print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!INSERT COMMITTED TO DATABASE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
#conn.rollback()
conn.close()
print ("Connection closed")
