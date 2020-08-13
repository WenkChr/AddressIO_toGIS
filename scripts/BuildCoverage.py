import os ,sys, arcpy, time
import pandas as pd
from arcgis.features import GeoAccessor
from arcgis.features import analysis

arcpy.env.overwriteOutput = True
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
workingGDB = r'H:\AddressIO_Home\workingGDB.gdb'
scratchGDB = r'H:\AddressIO_Home\scratch.gdb'
#-----------------------------------------------------------------------------------
# Logic
t0 = time.time()
prCodes = {'ab' : 48, 'bc' : 59, 'mb' : 46, 'nb' : 13, 'nl' : 10, 'ns' : 12, 'on' : 35, 
        'qc' : 24, 'sk' : 47, 'yt' : 60, 'pe' : 11, 'nt' : 61, 'nu' : 62}
# Loop to create provincial spatial joins in the scratch gdb
for prov in ('ab', 'bc', 'mb', 'nb', 'nl', 'ns', 'on', 'qc', 'sk', 'yt', 'pe', 'nt', 'nu'):
        provfc = os.path.join(workingGDB, f'{prov}_all')
        if not arcpy.Exists(provfc): continue #IF a file does not exist for a province then ignore it
        print(f'Creating coverage for {prov}')
        #csdlyr = arcpy.MakeFeatureLayer_management(csdPath, where_clause= f"PRUID = '{str(prCodes[prov])}'")
        alyr = arcpy.MakeFeatureLayer_management(os.path.join(workingGDB, f'{prov}_all'))
        arcpy.SpatialJoin_analysis(alyr, csdPath, os.path.join(scratchGDB, f'{prov}_sj'))
count_series = []
for prov in ('pe', 'ns', 'nl'):
        print(f'Getting counts for {prov}')
        fc = os.path.join(scratchGDB, f'{prov}_sj')
        df = pd.DataFrame.spatial.from_featureclass(fc)
        groups = df['CSDUID'].value_counts()
        del df
        count_series.append(groups)
        print(len(groups))

print(count_series)
csd_counts_df = pd.concat(count_series, names= ['AddressCount'])       
csddf = pd.DataFrame.spatial.from_featureclass(csdPath)
merged = pd.merge(csddf, csd_counts_df, left_on='CSDUID', right_index= True)
del csddf
merged.rename(columns= {'CSDUID_y' : 'AddressCount'}, inplace= True)
print(merged.head())
t1 = time.time() 
print(f'Total time taken to run script: {round((t1 - t0)/60, 2)} min')
print('DONE!')
