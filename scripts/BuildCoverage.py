import os ,sys
import pandas as pd
from arcgis.features import GeoAccessor


#-----------------------------------------------------------------------------------
#Inputs
csdPath = r'H:\AddressIO_Home\lcsd000b16a_e.shp'
provFilesGDB = r'H:\AddressIO_Home\workingGDB.gdb' 

#-----------------------------------------------------------------------------------
# Logic
prCodes = {'ab' : 48, 'bc' : 59, 'mb' : 46, 'nb' : 13, 'nl' : 10, 'ns' : 12, 'on' : 35, 
        'qc' : 24, 'sk' : 47, 'yt' : 60, 'pe' : 11, 'nt' : 61, 'nu' : 62}

csdDF = pd.DataFrame.spatial.from_featureclass(csdPath)
for prov in ['ab', 'bc', 'mb', 'nb', 'nl', 'ns', 'on', 'qc', 'sk', 'yt', 'pe', 'nt']:
     csdProvDF = csdDF.loc[csdDF.PRUID == prCodes[prov]]
     


print('DONE!')
