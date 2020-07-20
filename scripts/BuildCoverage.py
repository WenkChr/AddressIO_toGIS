import os ,sys
import pandas as pd
from arcgis.features import GeoAccessor
from arcgis.features import analysis


#-----------------------------------------------------------------------------------
#Inputs
csdPath = r'H:\AddressIO_Home\lcsd000b16a_e.shp'
provFilesGDB = r'H:\AddressIO_Home\workingGDB.gdb' 

#-----------------------------------------------------------------------------------
# Logic
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
                csddf = csdProvDF.loc[csdProvDF.CSDUID == row.CSDUID]
                print(csddf.head())
                print(f'Creating spatial index for CSD: {row.CSDNAME}')
                si = csdProvDF.spatial.sindex('quadtree', reset= False) # This kills you memory don't do this !!!!
                print('Looking for intersects between csd and address points')
                indexOfFeatures = pointsDF.intersect(bbox = si)
                print(len(indexOfFeatures))
                sys.exit()
        print(csdProvDF.head())
        sys.exit()

print('DONE!')
