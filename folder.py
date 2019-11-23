#Connect to folder
folder_path = r'C:\Users\samwieske\Desktop\folderpath'

#import the many modules I will be using 
import arcpy
import math
import os
from arcpy.sa import *

# Define workspace as your folder path 
arcpy.env.workspace = folder_path
# Allow overwriting output files
arcpy.env.overwriteOutput = True

#Define Inputs
#Vector data of cities or regions for buffer analysis

#Places = GetParameterAsText(0)
Places = r"C:\Users\samwieske\Desktop\folderpath\ne_10m_populated_places.shp"

#Raster DEM data for elevation analysis
#Region = GetParameterAsText(1)
Region = folder_path + "\LC08_L1TP_041036_20191021_20191030_01_T1_B1.tif"



#Step 1. Clip Places to Region

#Define raster extent output
rasPoly = r"C:\Users\samwieske\Desktop\folderpath\rasterpoly.shp"

#The raster datasets in the input workspace
in_raster_datasets = arcpy.ListRasters()

#sr = arcpy.SpatialReference(r"C:\Users\Fuaad Khan\Desktop\Lab3\LabData\LabData.mdx")
#Create a Polygon Feature Class
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

                                                                   
#Run Clip Analysis

in_features = Places
clip_features = rasPoly
clipCity = "clipCities.shp"

arcpy.Clip_analysis(in_features, clip_features, clipCity)                                    
                                    
                                    
#Step 2. Define Raster values
    #2A. Create NDVI to determine a vegetation scale
                                    
if arcpy.CheckOutExtension("Spatial") == "CheckedOut":
	RedBandF=arcpy.Raster(folder_path + '\LC08_L1TP_041036_20191021_20191030_01_T1_B4.tif')
	InfraredBandF=arcpy.Raster(folder_path + '\LC08_L1TP_041036_20191021_20191030_01_T1_B5.tif')
	RedBand=arcpy.sa.Float(RedBandF) #Must be redefined as floats, not integers
	RedBand.save("RedBand.TIF")
	InfraredBand=arcpy.sa.Float(InfraredBandF)
	InfraredBand.save("InfraredBand.TIF")
	output_raster = (InfraredBand - RedBand) / (RedBand + InfraredBand) #NDVI calculation
	output_raster.save("NDVI.TIF")

print "NDVI raster has been successfully computed."
                                    


#Step 4. Buffer around cities

#Step 5. Need Austin's help

#Step 6. Use an update cursor to 
