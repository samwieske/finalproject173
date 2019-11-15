#Connect to folder
folder_path = r'C:\Users\samwieske\Desktop\FinalProjectfolder - Copy'

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
Places = r'C:\Users\samwieske\Desktop\FinalProjectfolder - Copy\PopulatedPlaces'

#Raster DEM data for elevation analysis
#Region = GetParameterAsText(1)
Region = r'C:\Users\samwieske\Desktop\FinalProjectfolder - Copy\LosAngelesLandsat8'


#Optional: Demographic data - based on real estate property values (TIGER/LINE data)
#Optional: FIRMS - can convert vector to raster


#Define Outputs
#IdealCity= GetParameterAsText(2)
IdealCity = os.path.join(folder_path, "city.shp")
Table = os.path.join(folder_path, "city.dbf")

#Step 1. Clip Places to Region

#Step 2. Define Raster values
    #2A. Create NDVI to determine a vegetation scale
    #2B. Create Elevation values map

#Step3. Reclassify tool

#Step 4. Buffer around cities

#Step 5. Need Austin's help

#Step 6. Use an update cursor to 
