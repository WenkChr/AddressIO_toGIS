import os ,sys, arcpy, time
import pandas as pd
from arcgis.features import GeoAccessor
from arcgis.features import analysis

#-----------------------------------------------------------------------------------
#Functions

def projectFC(fc, outGDB, outName, outSpatRef):
        inSpatRef = arcpy.Describe(fc).spatialReference
        transform = arcpy.ListTransformations(arcpy.Describe(fc).spatialReference, outSpatRef)
        if len(transform) != 0:
                arcpy.env.geographicTransformation = transform[0]
        arcpy.Project_management(fc, os.path.join(outGDB, outName), outSpatRef, transform_method= transform[0])
        return os.path.join(outGDB, outName)

#-----------------------------------------------------------------------------------
#Inputs
csdPath = r'H:\AddressIO_Home\lcsd000b16a_e.shp'
provFilesGDB = r'H:\AddressIO_Home\workingGDB.gdb'
#-----------------------------------------------------------------------------------
# Logic
t0 = time.time()
prCodes = {'ab' : 48, 'bc' : 59, 'mb' : 46, 'nb' : 13, 'nl' : 10, 'ns' : 12, 'on' : 35, 
        'qc' : 24, 'sk' : 47, 'yt' : 60, 'pe' : 11, 'nt' : 61, 'nu' : 62}
print('Reading CSD file into memory')
csdDF = pd.DataFrame.spatial.from_featureclass(csdPath)
for prov in ['ab', 'bc', 'mb', 'nb', 'nl', 'ns', 'on', 'qc', 'sk', 'yt', 'pe', 'nt']:
        print('Creating coverage for', prov)
        csdProvDF = csdDF.loc[csdDF.PRUID == str(prCodes[prov])] # Look only at csds for the specific province
        pointsDF = pd.DataFrame.spatial.from_featureclass(os.path.join(provFilesGDB, prov + '_all'))
        print(f'Get intersect count for each csd in {prov}')
        for row in csdProvDF.itertuples():
                #Select csd and build bounding box
                csddf = csdProvDF.loc[csdProvDF.CSDUID == row.CSDUID]
                df_extent = csdDF.spatial.full_extent
                print(f'Creating spatial index for CSD: {row.CSDNAME}')
                si = csdProvDF.spatial.sindex('quadtree', reset= False) # This kills you memory don't do this !!!!
                print('Looking for intersects between csd and address points')
                indexOfFeatures = si.intersect(bbox =csdProvDF.spatial.full_extent)
                print(row.CSDNAME, len(indexOfFeatures))
                sys.exit()
        print(csdProvDF.head())
        sys.exit()
t1 = time.time() 
print(f'Total time taken to run script: {round((t1 - t0)/60, 2)} min')
print('DONE!')
