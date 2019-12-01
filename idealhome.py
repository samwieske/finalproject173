#Define working directory
#folder_path = GetParameterAsText(0)
folder_path = r'C:\Users\fuaadkhan\Documents\folderpath'

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
#Places = GetParameterAsText(1)
Places = r"C:\Users\fuaadkhan\Documents\folderpath\ne_10m_populated_places.shp"

#Region: Landsat Raster of Los Angeles
#Region = GetParameterAsText(2)
Region = folder_path + "\LC08_L1TP_041036_20191021_20191030_01_T1_B1.tif"

#Schools: School points of Los Angeles
#Schools = GetParameterAsText(3)
Schools = folder_path + "\LMS_Data_Public_20160114.shp"

#LA Metro Stops
#Metro = GetParameterAsText(3)
metroStops = r'C:\Users\fuaadkhan\Desktop\LA__Transit_Stops\LA_Stops_Enriched.shp'

#Step 1: NDVI
if arcpy.CheckOutExtension("Spatial") == "CheckedOut":
        RedBandF=arcpy.Raster(folder_path + '\LC08_L1TP_041036_20191021_20191030_01_T1_B4.tif')
        InfraredBandF=arcpy.Raster(folder_path + '\LC08_L1TP_041036_20191021_20191030_01_T1_B5.tif')
        RedBand=arcpy.sa.Float(RedBandF) #Must be redefined as floats, not integers
        RedBand.save("RedBand.TIF")
        InfraredBand=arcpy.sa.Float(InfraredBandF)
        InfraredBand.save("InfraredBand.TIF")
        output_raster = (InfraredBand - RedBand) / (RedBand + InfraredBand) #NDVI calculation
        output_raster.save("NDVI.TIF")
else:
    print "Arc License is not avilable"

    print("NDVI raster has been successfully computed.")

#Step 2: 
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

#Run Clip Analysis
    in_features = Places
    clip_features = "raspoly.shp"
    clipCity = "clipCities.shp"
    arcpy.Clip_analysis(in_features, clip_features, clipCity)                                    
    print("Cities Clipped...")                                    

#Step 4: 5 mile Buffer around cities and Clip Raster to Buffer Mask
    cityBuffer = "clipCities_Buffer.shp"
    arcpy.Buffer_analysis(clipCity, cityBuffer, "3 Miles") #change this to clipCity instead of ClipCity
    print("Buffer Created...")

#Step 5: Zonal statistics 
    outputTable = folder_path+"\NDVI_table.dbf"
    arcpy.gp.ZonalStatisticsAsTable_sa(cityBuffer, "NAME", "NDVI.TIF", outputTable, "DATA", "MEAN")
    print ("Zonal Statistics Table Created...")

#School Count
    arcpy.SpatialJoin_analysis(cityBuffer, Schools, "SpatialJoin.shp", "JOIN_ONE_TO_MANY", "KEEP_ALL", "", "INTERSECT")
    arcpy.Statistics_analysis("SpatialJoin.shp", "schoolStats.dbf", "Join_Count SUM","NAME")
    print ("School Count DBF Created...")

#Join schoolStats to NDVI Table
    arcpy.JoinField_management(in_data="NDVI_table.dbf", in_field="NAME", join_table="schoolStats.dbf", join_field="name", fields="FREQUENCY")
    print ("School Count Joined to NDVI Table...")
    
#Metro Count
    arcpy.SpatialJoin_analysis(cityBuffer, metroStops, "MetroSpatialJoin.shp", "JOIN_ONE_TO_MANY", "KEEP_ALL", "", "INTERSECT")
    arcpy.Statistics_analysis("MetroSpatialJoin.shp", "metroStats.dbf", "Join_Count SUM","NAME")
    print ("Metro Count DBF Created...")

#Join metroStats to NDVI Table
    arcpy.JoinField_management(in_data="NDVI_table.dbf", in_field="NAME", join_table="metroStats.dbf", join_field="name", fields="FREQUENCY")
    print ("Metro Count Joined to NDVI Table...")

    
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

        #Metro Count
        arcpy.SpatialJoin_analysis(Places, metroStops, "MetroSpatialJoin.shp", "JOIN_ONE_TO_MANY", "KEEP_ALL", "", "INTERSECT")
        arcpy.Statistics_analysis("MetroSpatialJoin.shp", "metroStats.dbf", "Join_Count SUM","NAME")
        print ("Metro Count DBF Created...")
        #Join metroStats to NDVI Table
        arcpy.JoinField_management(in_data="NDVITable.dbf", in_field="NAME", join_table="metroStats.dbf", join_field="name", fields="FREQUENCY")
        print ("Metro Count Joined to NDVI Table...")

else:
    print ("Invalid Input, shape type is: "+desc.shapeType(Places))

arcpy.AddField_management("NDVITable.dbf", "NumBus", "FLOAT")
arcpy.AddField_management("NDVITable.dbf", "NumSchools", "FLOAT")
arcpy.AddField_management("NDVITable.dbf", "FinalScore", "FLOAT")

arcpy.CalculateField_management("NDVITable.dbf", "NumBus", "!FREQUENCY! - 1","PYTHON")
arcpy.CalculateField_management("NDVITable.dbf", "NumSchools", "!FREQUENC_1! - 1","PYTHON")

arcpy.DeleteField_management("NDVITable.dbf", "FREQUENCY")
arcpy.DeleteField_management("NDVITable.dbf", "FREQUENC_1")

print(">> End of Script <<")


