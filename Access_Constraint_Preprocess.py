# -*- coding: utf-8 -*-
"""
Created on Wed Dec 07 19:19:18 2016

This code will be used to automate the pre-processing of WFP Access Constraint
Datasets into a simplified, hierarchized, and interconnected road networks,
ready to be built into a working network dataset
@author: Luis Suter
"""
#import modules and set workspace
import arcpy

arcpy.env.workspace = "E:\ArcGIS_Data\South_Sudan\ConTrack_Code.gdb"
arcpy.env.overwriteOutput = True

#set local varibales and backup the original file, as edited changes are permanent
AccessConstraint = arcpy.GetParameter(0)
AC_Backup = "E:\ArcGIS_Data\South_Sudan\ConTrack_Code.gdb\AC_20161104_backup"
arcpy.CopyFeatures_management(AccessConstraint, AC_Backup)

#make layer from feature class
arcpy.MakeFeatureLayer_management(AccessConstraint, "AC_lyr")

print "Extracting primary roads."

#extract the main roads
query = ' "CLASS" = \'Primary\' OR "CLASS" = \'Secondary\' OR "CLASS" = \'Tertiary\' OR "CLASS" = \'Local/Urban\' '
selection = arcpy.SelectLayerByAttribute_management("AC_lyr", "NEW_SELECTION", query)

#export selection as new shapefile
arcpy.CopyFeatures_management(selection, "E:\ArcGIS_Data\South_Sudan\ConTrack_Code.gdb\AC_20161104_SelectedRoads")

#make layer from feature class
arcpy.MakeFeatureLayer_management("E:\ArcGIS_Data\South_Sudan\ConTrack_Code.gdb\AC_20161104_SelectedRoads", "Selection_lyr")

print "Preparing for Network Integration." 

#add field for hierarchy numbers
arcpy.AddField_management("Selection_lyr", "Hierarchy", "SHORT", "", "", "", "hierarchy", "NULLABLE", "REQUIRED")


#assign appropriate hierarchy number based on road class for network dataset
#select the classes that participate in the calculation
fields = ["CLASS", "Hierarchy"]
#assign 1 to primary, 2 to secondary, and 3 to tertiary and local/urban
with arcpy.da.UpdateCursor("Selection_lyr", fields) as cursor:
    for row in cursor:
        if (row[0] == "Primary"):
            row[1] = 1
        elif (row[0] == "Secondary"):
            row[1]= 2
        elif (row[0] == "Tertiary"):
            row[1] = 3
        elif (row[0] == "Local/Urban"):
            row[1] = 3
        #update the table with the calculated values
        cursor.updateRow(row)

#extend lines to ensure endpoint connectivity
arcpy.ExtendLine_edit("Selection_lyr", "25 meters", "EXTENSION")



print "Updating Network."

#set local variables
road_input = "E:\ArcGIS_Data\South_Sudan\ConTrack_Code.gdb\SSD_Network\Road_Network"
topo_input = "E:\ArcGIS_Data\South_Sudan\ConTrack_Code.gdb\SSD_Network\SSD_Network_Topology"
network_dataset = "E:\ArcGIS_Data\South_Sudan\ConTrack_Code.gdb\SSD_Network\ConTrack_Network"

#delete old road network if it exists from a prior network and the assocaited feature class
if arcpy.Exists(network_dataset):
    arcpy.Delete_management(network_dataset)
if arcpy.Exists(topo_input):
    arcpy.Delete_management(topo_input)
if arcpy.Exists(road_input):
    arcpy.Delete_management(road_input)

#add roads to network feature dataset
arcpy.FeatureClassToFeatureClass_conversion("Selection_Lyr", "SSD_Network", "Road_Network")

#create network topology to get rid of dangles and redundant line extensions, then validate network
#create topology and add rule
arcpy.CreateTopology_management("SSD_Network", "SSD_Network_Topology")
arcpy.AddFeatureClassToTopology_management(topo_input, road_input, 1)
arcpy.AddRuleToTopology_management(topo_input, "Must Not Have Dangles (Line)", road_input)

#validate topology
arcpy.ValidateTopology_management(topo_input)

#notify user tool has executed
print "Preprocessing Finished and Network Dataset Input Updated. Please create and build a new network in ArcMap now, unfortunately this process cannot be automated."