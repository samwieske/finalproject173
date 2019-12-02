#Authors: Fuaad Khan, Sam Wieske
#Define working directory
#folder_path: Where the input and output data will be stored
folder_path = arcpy.GetParameterAsText(0)
#folder_path = r'C:\Users\Fuaad Khan\Desktop\final\folderpath'

#Import Libraries
import arcpy
import math
import os
from arcpy.sa import *

#Set workspace as your folder path and allow overwrite
arcpy.env.workspace = folder_path
arcpy.env.overwriteOutput = True

#Define Inputs
#Places: City Shapefile
Places = arcpy.GetParameterAsText(1)
#Places = r"C:\Users\Fuaad Khan\Desktop\final\folderpath\LACN.shp"

#Region: Landsat Raster of Los Angeles
Region = arcpy.GetParameterAsText(2)
#Region = folder_path + "\LC08_L1TP_041036_20191021_20191030_01_T1_B1.tif"

#b4: Band 4 from the Landsat Raster
b4 = arcpy.GetParameterAsText(3)

#b5: Band 5 from the Landsat Raster
b5 = arcpy.GetParameterAsText(4)

#Schools: School points of Los Angeles
Schools = arcpy.GetParameterAsText(5)
#Schools = folder_path + "\LMS_Data_Public_20160114.shp"

#Bus Stops
busStops = arcpy.GetParameterAsText(6)
#busStops = r'C:\Users\Fuaad Khan\Desktop\final\folderpath\LA_Stops_Enriched.shp'

#uBuffer: User's input buffer area
uBuffer = arcpy.GetParameterAsText(7)

#Step 1: NDVI
if arcpy.CheckOutExtension("Spatial") == "CheckedOut":
    RedBandF=arcpy.Raster(b4)
    InfraredBandF=arcpy.Raster(b5)
    RedBand=arcpy.sa.Float(RedBandF) #Must be redefined as floats, not integers
    RedBand.save("RedBand.TIF")
    InfraredBand=arcpy.sa.Float(InfraredBandF)
    InfraredBand.save("InfraredBand.TIF")
    output_raster = (InfraredBand - RedBand) / (RedBand + InfraredBand) #NDVI calculation
    output_raster.save("NDVI.TIF")
else:
    print("Arc License is not avilable")

    print("NDVI raster has been successfully computed.")

#Step 2: Create a polygon boundary for future clipping of vector data to the raster region

#Check for input vector data type: Point or Polygon
desc=arcpy.Describe(Places)
if desc.shapeType == "Point": 
    print ("Shape Type: Point")

    #List of raster datasets in the input workspace
    in_raster_datasets = arcpy.ListRasters()

    #Create a polygon feature class for raster boundary
    arcpy.CreateFeatureclass_management(folder_path,"raspoly.shp","POLYGON", spatial_reference = Region)                                 
    arcpy.AddField_management("raspoly.shp","RasterName", "String","","",250)
    arcpy.AddField_management("raspoly.shp","RasterPath", "String","","",250)
    cursor = arcpy.InsertCursor("raspoly.shp")
    point = arcpy.Point()
    array = arcpy.Array()
    corners = ["lowerLeft", "lowerRight", "upperRight", "upperLeft"]

    for Ras in in_raster_datasets:
        feat = cursor.newRow()  
        r = arcpy.Raster(Ras)
        for corner in corners:    
            point.X = getattr(r.extent, "%s" % corner).X
            point.Y = getattr(r.extent, "%s" % corner).Y
            array.add(point)
        array.add(array.getObject(0))
        polygon = arcpy.Polygon(array)
        feat.shape = polygon
        feat.setValue("RasterName", Ras)
        feat.setValue("RasterPath", folder_path + "\\" + Ras)
        cursor.insertRow(feat)
        array.removeAll()
    del feat
    del cursor 

    print("RasterPoly Created...")                                                                   

    #Step 3: Run Clip Analysis
    in_features = Places
    clip_features = "raspoly.shp"
    clipCity = "clipCities.shp"
    arcpy.Clip_analysis(in_features, clip_features, clipCity)                                    
    print("Cities Clipped...")                                    

    #Step 4: 5 mile Buffer around cities and Clip Raster to Buffer Mask
    cityBuffer = "clipCities_Buffer.shp"
    arcpy.Buffer_analysis(clipCity, cityBuffer, uBuffer) #change this to clipCity instead of ClipCity
    print("Buffer Created...")

    #Step 5: Zonal statistics 
    outputTable = folder_path+"\NDVI_table.dbf"
    arcpy.gp.ZonalStatisticsAsTable_sa(cityBuffer, "NAME", "NDVI.TIF", outputTable, "DATA", "MEAN")
    print ("Zonal Statistics Table Created...")

    #Step 6: School Count
    arcpy.SpatialJoin_analysis(cityBuffer, Schools, "SpatialJoin.shp", "JOIN_ONE_TO_MANY", "KEEP_ALL", "", "INTERSECT")
    arcpy.Statistics_analysis("SpatialJoin.shp", "schoolStats.dbf", "Join_Count SUM","NAME")
    print ("School Count DBF Created...")

    #Step 7: Join schoolStats to NDVI Table
    arcpy.JoinField_management(in_data="NDVI_table.dbf", in_field="NAME", join_table="schoolStats.dbf", join_field="name", fields="FREQUENCY")
    print ("School Count Joined to NDVI Table...")
    
    #Step 8: Bus Stop Count
    arcpy.SpatialJoin_analysis(cityBuffer, busStops, "BusSpatialJoin.shp", "JOIN_ONE_TO_MANY", "KEEP_ALL", "", "INTERSECT")
    arcpy.Statistics_analysis("BusSpatialJoin.shp", "BusStats.dbf", "Join_Count SUM","NAME")
    print ("Bus Count DBF Created...")

    #Step 9: Join BusStats to NDVI Table
    arcpy.JoinField_management(in_data="NDVI_table.dbf", in_field="NAME", join_table="BusStats.dbf", join_field="name", fields="FREQUENCY")
    print ("Bus Count Joined to NDVI Table...")

    
############################################################################################################    
elif desc.shapeType == "Polygon":
    print("Shape Type: Polygon")
    #NDVI -> Table
    outputTable = folder_path + "\NDVITable.dbf"
    arcpy.gp.ZonalStatisticsAsTable_sa(Places, "NAME", "NDVI.TIF", outputTable, "DATA", "MEAN")
    print ("Zonal Statistics Table Created...")

    #School Count
    arcpy.SpatialJoin_analysis(Places, Schools, "SpatialJoin.shp", "JOIN_ONE_TO_MANY", "KEEP_ALL", "", "INTERSECT")
    arcpy.Statistics_analysis("SpatialJoin.shp", "schoolStats.dbf", "Join_Count SUM","NAME")
    print ("School Count DBF Created...")

    #Join schoolStats to NDVI Table
    arcpy.JoinField_management(in_data="NDVITable.dbf", in_field="NAME", join_table="schoolStats.dbf", join_field="name", fields="FREQUENCY")
    print ("School Count Joined to NDVI Table...")

    #Bus Count
    arcpy.SpatialJoin_analysis(Places, busStops, "BusSpatialJoin.shp", "JOIN_ONE_TO_MANY", "KEEP_ALL", "", "INTERSECT")
    arcpy.Statistics_analysis("BusSpatialJoin.shp", "BusStats.dbf", "Join_Count SUM","NAME")
    print ("Metro Count DBF Created...")
    
    #Join BusStats to NDVI Table
    arcpy.JoinField_management(in_data="NDVITable.dbf", in_field="NAME", join_table="BusStats.dbf", join_field="name", fields="FREQUENCY")
    print ("Bus Count Joined to NDVI Table...")

else:
    print ("Invalid Input, shape type is: "+desc.shapeType(Places))

arcpy.AddField_management("NDVITable.dbf", "NumBus", "FLOAT")
arcpy.AddField_management("NDVITable.dbf", "NumSchools", "FLOAT")
#arcpy.AddField_management("NDVITable.dbf", "FinalScore", "FLOAT")

arcpy.CalculateField_management("NDVITable.dbf", "NumBus", "!FREQUENCY! - 1","PYTHON")
arcpy.CalculateField_management("NDVITable.dbf", "NumSchools", "!FREQUENC_1! - 1","PYTHON")

arcpy.DeleteField_management("NDVITable.dbf", "FREQUENCY")
arcpy.DeleteField_management("NDVITable.dbf", "FREQUENC_1")
arcpy.DeleteField_management("NDVITable.dbf", "COUNT")
arcpy.DeleteField_management("NDVITable.dbf", "ZONE_CODE")

arcpy.AddField_management("NDVITable.dbf", "Bus_Scr", "FLOAT")
arcpy.AddField_management("NDVITable.dbf", "Mean_Scr", "FLOAT")
arcpy.AddField_management("NDVITable.dbf", "Schl_Scr", "FLOAT")
arcpy.AddField_management("NDVITable.dbf", "Final_Scr", "FLOAT")

#meanScore=arcpy.da.InsertCursor("NDVITable.dbf", ("MeanScore"))

with arcpy.da.UpdateCursor("NDVITable.dbf", ("MEAN","Mean_Scr")) as Mean:

    for x in Mean:
        if (x[0] >= 0.0 and x[0] <= 0.06):
            x[1] = 1
        elif (x[0] > 0.06 and x[0] <= 0.115):
            x[1] = 2
        elif (x[0] > 0.115 and x[0] <= 0.17):
            x[1] = 3
        elif (x[0] > 0.17):
            x[1] = 4
            
        Mean.updateRow(x)

del Mean, x

with arcpy.da.UpdateCursor("NDVITable.dbf", ("NumBus","Bus_Scr")) as Bus:

    for x in Bus:
        if (x[0] >= 0.0 and x[0] <= 200.0):
            x[1] = 1
        elif (x[0] > 200.0 and x[0] <= 800.0):
            x[1] = 2
        elif (x[0] > 800.0 and x[0] <= 1597.0):
            x[1] = 3
        elif (x[0] > 1597.0):
            x[1] = 4
            
        Bus.updateRow(x)
        
del Bus, x

with arcpy.da.UpdateCursor("NDVITable.dbf", ("NumSchools","Schl_Scr")) as School:

    for x in School:
        if (x[0] == 0.0):
            x[1] = 0
        if (x[0] > 0.0 and x[0] <= 125.0):
            x[1] = 1
        elif (x[0] > 125.0 and x[0] <= 250.0):
            x[1] = 2
        elif (x[0] > 250.0 and x[0] <= 375.0):
            x[1] = 3
        elif (x[0] > 375.0):
            x[1] = 4
            
        School.updateRow(x)
        
del School, x

with arcpy.da.UpdateCursor("NDVITable.dbf", ("Mean_Scr","Bus_Scr","Schl_Scr", "Final_Scr")) as Final:

    for x in Final:
        x[3] = (3*(x[0]))+(2*(x[1]))+(x[2])
            
        Final.updateRow(x)
        
del Final, x
        
#Copy and clean finaltable

arcpy.Copy_management("NDVITable.dbf", "IdealHome.dbf")

arcpy.DeleteField_management("IdealHome.dbf", "Mean_Scr")
arcpy.DeleteField_management("IdealHome.dbf", "Bus_Scr")
arcpy.DeleteField_management("IdealHome.dbf", "Schl_Scr")

print(">> End of Script <<")


