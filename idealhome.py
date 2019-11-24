#Define working directory
#folder_path = GetParameterAsText(0)
folder_path = r'C:\Users\samwieske\Desktop\folderpath'

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
Places = r"C:\Users\samwieske\Desktop\folderpath\ne_10m_populated_places.shp"

#Region: Landsat Raster of Los Angeles
#Region = GetParameterAsText(2)
Region = folder_path + "\LC08_L1TP_041036_20191021_20191030_01_T1_B1.tif"


#Step 1: Clip Places to Region

#Define output shapefile for the raster's polygon boundary
rasPoly = r"C:\Users\samwieske\Desktop\folderpath\rasterpoly.shp"

#List of raster datasets in the input workspace
in_raster_datasets = arcpy.ListRasters()

#Create a polygon feature class for raster boundary
arcpy.CreateFeatureclass_management(os.path.dirname(rasPoly),os.path.basename(rasPoly),"POLYGON", spatial_reference = Region)
                                    
arcpy.AddField_management(rasPoly,"RasterName", "String","","",250)
arcpy.AddField_management(rasPoly,"RasterPath", "String","","",250)

cursor = arcpy.InsertCursor(rasPoly)
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
clip_features = rasPoly
clipCity = "clipCities.shp"

arcpy.Clip_analysis(in_features, clip_features, clipCity)                                    
                                    
print("Cities Clipped...")                                    
#Step 2: Define Raster values
    #2A: Create NDVI to determine a vegetation scale
                                    
if arcpy.CheckOutExtension("Spatial") == "CheckedOut":
	RedBandF=arcpy.Raster(folder_path + '\LC08_L1TP_041036_20191021_20191030_01_T1_B4.tif')
	InfraredBandF=arcpy.Raster(folder_path + '\LC08_L1TP_041036_20191021_20191030_01_T1_B5.tif')
	RedBand=arcpy.sa.Float(RedBandF) #Must be redefined as floats, not integers
	RedBand.save("RedBand.TIF")
	InfraredBand=arcpy.sa.Float(InfraredBandF)
	InfraredBand.save("InfraredBand.TIF")
	output_raster = (InfraredBand - RedBand) / (RedBand + InfraredBand) #NDVI calculation
	output_raster.save("NDVI.TIF")

print("NDVI raster has been successfully computed.")
                                    


#Step 4: 5 mile Buffer around cities and Clip Raster to Buffer Mask
cityBuffer = "clipCities_Buffer.shp"
arcpy.Buffer_analysis(ClipCity, cityBuffer, "5 Miles")
print("Buffer Created...")

arcpy.gp.ExtractByMask_sa("NDVI.TIF", cityBuffer)
print("Raster Mask Extracted...")

print(">> End of Script <<")
#Step 5: Zonal statistics on extracted masks
#Step 6: Use an update cursor to add stats to clipped cities shapefile 
