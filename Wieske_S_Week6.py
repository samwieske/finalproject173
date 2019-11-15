
#Connect to folder
folder_path = r'C:\Users\Sam Wieske\Desktop\LabData\LabData'

#import the many modules I will be using 
import arcpy
import math
import os
from arcpy.sa import *

# Define workspace as your folder path 
arcpy.env.workspace = folder_path
# Allow overwriting output files
arcpy.env.overwriteOutput = True

#Step 1. Print out properties for the Landsat image, using the Describe tool
raster = "Landsat.tif"
desc= arcpy.Describe(raster)
print raster + " - Projection Type: " + desc.spatialReference.Name
print "Number of Bands:" + str(desc.bandCount)
desc= arcpy.Describe(raster + '/Band_1')
print "Height:" + str(desc.height)
print "Width:" + str(desc.width)
print "Resolution:" + str(desc.meanCellHeight)+ " " + str(desc.spatialReference.linearUnitName)+ "s"



#Create an empty output raster to add to
output_raster = os.path.join(folder_path, "output.shp")

#Step 2. Compute the NDVI Raster
if arcpy.CheckOutExtension("Spatial") == "CheckedOut":
	RedBandF=arcpy.Raster(raster +'/Band_3')
	InfraredBandF=arcpy.Raster(raster +'/Band_4')
	RedBand=arcpy.sa.Float(RedBandF) #Must be redefined as floats, not integers
	RedBand.save("RedBand.TIF")
	InfraredBand=arcpy.sa.Float(InfraredBandF)
	InfraredBand.save("InfraredBand.TIF")
	output_raster = (InfraredBand - RedBand) / (RedBand + InfraredBand) #NDVI calculation
	output_raster.save("NDVI.TIF")

print "NDVI raster has been successfully computed."

#Step 3
    #Generate a NDVI category raster using different ranges
    #Reclassify/Remap tool
	
#Define inputs
inRaster = "NDVI.TIF"
field = "Value"
myremap = arcpy.sa.RemapRange([[-0.7,0,1],[0,0.3,2], [0.3,1, 3]]) #The lowest value is larger than -0.7


# Execute Reclassify
outReclass = Reclassify(inRaster, field, myremap)
outReclass.save("outReclass.TIF")

print "NDVI Category raster has been created."

#Step 4
    #From the Raster you created, to show that you did everything correct
    #Find the NDVI at location: (349908,376885)

Result = arcpy.GetCellValue_management(inRaster, "349908 3768856", "1")

cellSize = Result.getOutput(0)

# View the result in execution log
print "At 349908 3768856 Lat and Long, the cell value is  " + cellSize

                       
#Delete variables
del inRaster, myremap, raster
print "All Done."


