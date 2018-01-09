# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 13:09:15 2016

This is the execution of the ConTrack Program Code. It will take user input in the form of two points from a predetermined list of locations. 
For this proof of concept it will be  key towns, but users would be able to create their own locations, like Office HQs or Project Sites, 
through an individualized profile. The code will then plot the shortest route between these locations and create an automated report with 
a focused map of the route, and a country wide profile. Road Access Constraint data, provided by the UN Logistics Cluster, along the route
will be analyzed and be reported in both visual and text form. The initial purpose of this program is facilitate Security Officers of Log-
istics planners working in unsecure environments, by automating the laborious manual plotting and analysis of convoy routes and creating 
a common operational picture.

The program will and plans to be expanded to include the ability to see other organizations planning similar routes to facilitate convoy 
coordination between humanitarian and development actors working in an area. The final product of this application development would also
include a way to incorporate user feedback on route conditions into the Access Constraint database, to improve the accuracy and detail of 
this important logistical planning data.
@author: Luis Suter
"""
#import modules, check out Network Analyst, and set workspace
import arcpy
from arcpy import mapping
arcpy.env.workspace = "E:\ArcGIS_Data\South_Sudan\ConTrack_Code.gdb"
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Network")

#set variables for analysis including user input for Origin and Destination Towns
network_dataset = "E:\ArcGIS_Data\South_Sudan\ConTrack_Code.gdb\SSD_Network\ConTrack_Network"
locations_layer = "Key_Towns"
AC = "E:\ArcGIS_Data\South_Sudan\ConTrack_Code.gdb\AC_20161104_SelectedRoads"
Trip_Table = arcpy.mapping.TableView("Trips")
outputRoute = "E:\ArcGIS_Data\South_Sudan\ConTrack_Code.gdb\Route_Export"
Road_Network = "E:\ArcGIS_Data\South_Sudan\ConTrack_Code.gdb\SSD_Network\Road_Network"

#define parameters (eventually add User input to Table of Trips)
user_name = arcpy.GetParameterAsText(0)
origin = arcpy.GetParameterAsText(1)
destination = arcpy.GetParameterAsText(2)
travel_date = arcpy.GetParameter(3)
start_trav_window = arcpy.GetParameter(4)
end_trav_window = arcpy.GetParameter(5)

    
#build query for extracting the two locations in the trip
query = """ "Town_Name" = '%s' OR "Town_Name" = '%s' """ %(origin, destination)

#make feature layer from locations
arcpy.MakeFeatureLayer_management(locations_layer, "Locations")

#select layer by attribute and copy selected features to new layer
arcpy.SelectLayerByAttribute_management("Locations", "NEW_SELECTION", query)
arcpy.CopyFeatures_management("Locations", "Trip_Temp")

#create a Network Analyst route layer
arcpy.na.MakeRouteLayer(network_dataset, "Route", "Length", "FIND_BEST_ORDER", "", "", "", "ALLOW_UTURNS", "", "USE_HIERARCHY", "", "TRUE_LINES_WITH_MEASURES", "")

#add origin and destination to route, solve for best path
arcpy.AddLocations_na("Route", "Stops", "Trip_Temp", "", 100)
arcpy.na.Solve("Route")
    
#clip AccessConstraint data by the route to isolate Route Specific Data on conditions etc
arcpy.Clip_analysis(AC, "Route\Routes", outputRoute)    

#Trip coordination analysis, store that in a new table
Coord_query = """ "Origin" = '%s' AND "Destination" = '%s' AND "Travel_Date" >= date '%s' AND "Travel_Date" <= date '%s' """ %(origin, destination, start_trav_window, end_trav_window)
#select features in from trip database with the same origin and destination, as well as a desired travel date within the travel windows of other trips
arcpy.SelectLayerByAttribute_management(Trip_Table, "NEW_SELECTION", Coord_query)
#create summary statistics table with list of users
arcpy.Statistics_analysis(Trip_Table, "coord_stats", [["OBJECTID", "COUNT"]], "User")

#add current trip to trip database
count = int(arcpy.GetCount_management(Trip_Table).getOutput(0))
cursor = arcpy.InsertCursor(Trip_Table)
for i in range(count, count + 1):
    row = cursor.newRow()
    row.setValue("User", user_name)
    row.setValue("Origin", origin)
    row.setValue("Destination", destination)
    row.setValue("Travel_Date", travel_date)
    row.setValue("Window_Start", start_trav_window)
    row.setValue("Window_End", end_trav_window)
    cursor.insertRow(row)
    
#add row (kilometers) to output route table, and caluclate based off Shape Length
arcpy.AddField_management(outputRoute, "Kilometers", "FLOAT", 9, 2, "", "", "NULLABLE", "REQUIRED")
arcpy.CalculateField_management(outputRoute, "Kilometers", '[SHAPE_Leng] / 1000')

#Road  Analysis, for surface, condition, vehicle rec statistics, to get kilometer values in each classification
arcpy.Statistics_analysis(outputRoute, "surface_stats", [["Kilometers", "SUM"]], "SURFACE")
arcpy.Statistics_analysis(outputRoute, "rainy_stats", [["Kilometers", "SUM"]], "RAINYSTAT")
arcpy.Statistics_analysis(outputRoute, "prac_stats", [["Kilometers", "SUM"]], "PRAC")
arcpy.Statistics_analysis(outputRoute, "cond_stats", [["Kilometers", "SUM"]], "CONDITION")

#Create automated report with map etc
#set all necessary variables
#label the mapping document and the dataframes
mxd = arcpy.mapping.MapDocument("E:\ArcGIS_Data\South_Sudan\ConTrack_Template.mxd")
df = arcpy.mapping.ListDataFrames(mxd)[0]
df2 = arcpy.mapping.ListDataFrames(mxd)[1]
reference = arcpy.mapping.Layer("Admin")
#create mapping layers from the premade road symbology layers
Road_symbology = arcpy.mapping.Layer("E:\ArcGIS_Data\South_Sudan\Sudan_symbology\Road_Symbology.lyr")
AC_symbology = arcpy.mapping.Layer("E:\ArcGIS_Data\South_Sudan\Sudan_symbology\AC_Symbology.lyr")
Route_symbology = arcpy.mapping.Layer("E:\ArcGIS_Data\South_Sudan\Sudan_symbology\Route_Symbology.lyr")
Key_Towns_symbology = arcpy.mapping.Layer("E:\ArcGIS_Data\South_Sudan\Sudan_symbology\Key_Towns_Symbology.lyr")
#add the road network and the temporary routes, as well as the Access Constraint data
insertAC = arcpy.mapping.Layer(AC)
insertRoads = arcpy.mapping.Layer(Road_Network)
insertRoute = arcpy.mapping.Layer(outputRoute)
insertTowns = arcpy.mapping.Layer("Key_Towns")
#get extents of the route as well as South Sudan Country
ext = insertRoute.getExtent()
ext2 = reference.getExtent()
#create table views of the route analyis tables
surface_table = arcpy.mapping.TableView("surface_stats")
condition_table = arcpy.mapping.TableView("cond_stats")
rainy_table = arcpy.mapping.TableView("rainy_stats")
vehc_table = arcpy.mapping.TableView("prac_stats")
coord_table = arcpy.mapping.TableView("coord_stats")

#turn on labels for towns
#this needs to be improved. Ideally the comments would be in text boxes around the edge of the map.
#tried to use UpdateLayer properties to get the labeling to work better, but it doesn't fully work.
#this way displays some labels, but not those with long text...
insertTowns.showLabels = True
if insertRoute.supports("LABELCLASSES"):
    for lblclass in insertRoute.labelClasses:
            lblclass.className = "Comments"
            lblclass.expression = '"%s" & [COMMENT] & "%s"' % ("<CLR red='255' green='0' blue='0'>", "</CLR>")
    lblclass.showClassLabels = True
insertRoute.showLabels = True

#apply symbology from symboloy templates in the symbology folder
arcpy.ApplySymbologyFromLayer_management(insertAC, AC_symbology)
arcpy.ApplySymbologyFromLayer_management(insertRoads, Road_symbology)
arcpy.ApplySymbologyFromLayer_management(insertRoute, Route_symbology)
arcpy.ApplySymbologyFromLayer_management(insertTowns, Key_Towns_symbology)


#add the layers to the dataframe of the zoomed in route view and zoom to the extent of the route
#need to work on the zoom to extent because it cut off the labels of the map a bit...
arcpy.mapping.AddLayer(df, insertAC, "TOP")
arcpy.mapping.AddLayer(df, insertRoads, "TOP")
arcpy.mapping.AddLayer(df, insertRoute, "TOP")
arcpy.mapping.AddLayer(df, insertTowns, "TOP")
df.extent = ext


#create country map
#here using the extent of South Sudan as a country creates a good scale. Need to adjust labeling in this dataframe. 
#as mentioned before the labeling is quite hard to do through arcpy
arcpy.mapping.AddLayer(df2, insertAC, "TOP")
arcpy.mapping.AddLayer(df2, insertRoads, "TOP")
arcpy.mapping.AddLayer(df2, insertRoute, "TOP")
arcpy.mapping.AddLayer(df2, insertTowns, "TOP")
df2.extent = ext2

#add table views of the route analysis view the dataframe
arcpy.mapping.AddTableView(df, surface_table)
arcpy.mapping.AddTableView(df, condition_table)
arcpy.mapping.AddTableView(df, rainy_table)
arcpy.mapping.AddTableView(df, vehc_table)

#create reports from the table views, using premade report templates, create tifs of these reports
arcpy.mapping.ExportReport(surface_table, "E:\ArcGIS_Data\South_Sudan\Reports\Surface_Layout.rlf", r"E:\ArcGIS_Data\South_Sudan\Reports\Surface_Report.tif")
arcpy.mapping.ExportReport(condition_table, "E:\ArcGIS_Data\South_Sudan\Reports\Condition_Layout.rlf", r"E:\ArcGIS_Data\South_Sudan\Reports\Condition_Report.tif")
arcpy.mapping.ExportReport(rainy_table, "E:\ArcGIS_Data\South_Sudan\Reports\Rainy_Layout.rlf", r"E:\ArcGIS_Data\South_Sudan\Reports\Rainy_Report.tif")
arcpy.mapping.ExportReport(vehc_table, "E:\ArcGIS_Data\South_Sudan\Reports\Vehicle_Layout.rlf", r"E:\ArcGIS_Data\South_Sudan\Reports\Vehicle_Report.tif")
arcpy.mapping.ExportReport(coord_table,"E:\ArcGIS_Data\South_Sudan\Reports\Coord_Layout.rlf", r"E:\ArcGIS_Data\South_Sudan\Reports\Partner_Report.tif" )

#insert route report tifs into layout, picture "slots" had to be instersted into the mapping document before
for pic in arcpy.mapping.ListLayoutElements(mxd, "PICTURE_ELEMENT"):
    if pic.name == "Surface":
        pic.sourceImage = "E:\ArcGIS_Data\South_Sudan\Reports\Surface_Report.tif"
        pic.elementHeight = 2.6896
        pic.elementWidth = 3.387
        pic.elementPositionX = 0.2738
        pic.elementPositionY = 1.555
    elif pic.name == "Condition":
        pic.sourceImage = "E:\ArcGIS_Data\South_Sudan\Reports\Condition_Report.tif"
        pic.elementHeight = 2.6896
        pic.elementWidth = 3.387
        pic.elementPositionX = 2.3002
        pic.elementPositionY = 1.555
    elif pic.name == "Vehicle":
        pic.sourceImage = "E:\ArcGIS_Data\South_Sudan\Reports\Vehicle_Report.tif"
        pic.elementHeight = 2.6896
        pic.elementWidth = 3.387
        pic.elementPositionX = 4.5067
        pic.elementPositionY = 1.555
    elif pic.name == "Rainy":
        pic.sourceImage = "E:\ArcGIS_Data\South_Sudan\Reports\Rainy_Report.tif"
        pic.elementHeight = 2.6896
        pic.elementWidth = 3.387
        pic.elementPositionX = 6.7754
        pic.elementPositionY = 1.555
    elif pic.name == "Partners":
        pic.sourceImage = "E:\ArcGIS_Data\South_Sudan\Reports\Partner_Report.tif"
        pic.elementHeight = 2.6896
        pic.elementWidth = 3.387
        pic.elementPositionX = 8.9434
        pic.elementPositionY = 1.555
        
#add title
for text_box in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
    if text_box.name == "TitleText":
        text_box.text = " ConTrack Route Report: %s to %s \n %s %s " %(origin, destination, travel_date, user_name)
        
#export map / report
save_file = "E:\ArcGIS_Data\South_Sudan\Final_Maps\%s_%s_%s_%s" %(origin, destination, user_name, count)
arcpy.mapping.ExportToPDF(mxd, save_file)

#delete temp layesrs
arcpy.Delete_management("Trip_Temp")
arcpy.Delete_management(outputRoute)
arcpy.Delete_management("surface_stats")
arcpy.Delete_management("cond_stats")
arcpy.Delete_management("rainy_stats")
arcpy.Delete_management("prac_stats")
arcpy.Delete_management("coord_stats")

