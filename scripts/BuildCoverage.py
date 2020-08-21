import os ,sys, arcpy, time
import pandas as pd
from arcgis.features import GeoAccessor
from dotenv import load_dotenv
from pathlib import Path
arcpy.env.overwriteOutput = True
#-----------------------------------------------------------------------------------
#Input
BASEDIR = os.getcwd()
load_dotenv(os.path.join(BASEDIR, 'environments.env'))
homepath = os.getenv('OUT_DIR')
csdPath = os.getenv('CSD_PATH')
provFilesGDB = os.path.join(Path(os.getenv('OUT_DIR')), 'workingGDB.gdb')
workingGDB = os.path.join(Path(os.getenv('OUT_DIR')), 'workingGDB.gdb')
scratchGDB = os.getenv('SCRATCH_GDB')
#-----------------------------------------------------------------------------------
# Logic
t0 = time.time()
prCodes = {'ab' : 48, 'bc' : 59, 'mb' : 46, 'nb' : 13, 'nl' : 10, 'ns' : 12, 'on' : 35, 
        'qc' : 24, 'sk' : 47, 'yt' : 60, 'pe' : 11, 'nt' : 61, 'nu' : 62}
#Create scratch GDB if it doesn't exist
if not arcpy.Exists(scratchGDB):
        print('Creating Scratch GDB')
        arcpy.CreateFileGDB_management(os.path.split(scratchGDB)[0], os.path.split(scratchGDB)[1])
# Loop to create provincial spatial joins in the scratch gdb
for prov in ('ab', 'bc', 'mb', 'nb', 'nl', 'ns', 'on', 'qc', 'sk', 'yt', 'pe', 'nt', 'nu'):
        provfc = os.path.join(workingGDB, f'{prov}_all')
        if not arcpy.Exists(provfc): continue #IF a file does not exist for a province then ignore it
        print(f'Creating spatial join between CSDs and {prov}')
        alyr = arcpy.MakeFeatureLayer_management(os.path.join(workingGDB, f'{prov}_all'))
        arcpy.SpatialJoin_analysis(alyr, csdPath, os.path.join(scratchGDB, f'{prov}_sj'))
count_series = []
for prov in ('on', 'ab', 'bc', 'mb', 'nb', 'nl', 'ns', 'qc', 'sk', 'yt', 'pe', 'nt', 'nu'): # 'on' removed because of memory issues loading points into memory
        if not arcpy.Exists(os.path.join(scratchGDB, f'{prov}_sj')): continue
        print(f'Getting counts for {prov}')
        fc = os.path.join(scratchGDB, f'{prov}_sj')
        if prov == 'on':
                ids = pd.DataFrame.spatial.from_featureclass(csdPath, columns= ['PRUID', 'CSDUID'], where_clause= "PRUID = '35'")
                for cid in ids['CSDUID'].tolist():
                        print(f'Getting count for CSDUID: {cid}')
                        df = pd.DataFrame.spatial.from_featureclass(fc, columns= ['CSD_UID'], where_clause= f"CSDUID = '{cid}'")
                        groups = df['CSDUID'].value_counts()
                        del df
                        count_series.append(groups)

        else:
                df = pd.DataFrame.spatial.from_featureclass(fc, columns= ['CSDUID'])
                groups = df['CSDUID'].value_counts()
                del df
                count_series.append(groups)

csd_counts_df = pd.concat(count_series, axis= 0)       
csddf = pd.DataFrame.spatial.from_featureclass(csdPath)
merged = pd.merge(csddf, csd_counts_df, left_on='CSDUID', right_index= True)
del csddf
merged.rename(columns= {'CSDUID_y' : 'AddressCount'}, inplace= True)
merged.drop(['CSDUID_x', 'FID'], axis= 1, inplace= True)
merged.spatial.to_featureclass(os.path.join(workingGDB, 'DataCoverage'), overwrite= True)
t1 = time.time() 
print(f'Total time taken to run script: {round((t1 - t0)/60, 2)} min')
print('DONE!')
