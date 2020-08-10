import os, sys,  requests, time, urllib, shutil, glob, time, arcpy
import pandas as pd
from zipfile import ZipFile
from arcgis import GeoAccessor

arcpy.env.OverwriteOutput = True
#--------------------------------------------------------------------------------------------------------------------------------------
''' Workflow Overview:
1.) Download state.txt from openaddressIO and compare the address counts for each Canada file to the counts for the current csv files
2.) If the counts are different then flag the file for updating
3.) Download all flagged files and update the csv file in the current file structure
4.) Recreate the point file and the csd coverage files for the provinces that have updates address files
'''
#--------------------------------------------------------------------------------------------------------------------------------------
# function definitions
def check_url_exists(url):
    import urllib3
    http = urllib3.PoolManager()
    request = http.request('GET', url)
    if request.status == 200:
        print('Website Exists')
    else:
        print('Error with site.')
        print('Status Code: ' + str(request.status))
        print('Fix error then restart script')
        sys.exit()

def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts
#--------------------------------------------------------------------------------------------------------------------------------
# inputs
Data_GDB = 'H:\\AddressIO_Home\\workingGDB.gdb'
OpenIO_zip = "https://data.openaddresses.io/openaddr-collected-north_america.zip"
intermediateZipFolder = 'H:\\AddressIO_Home\\IntermediateZips'
Old_Data = 'H:\AddressIO_Home\openaddr-collected-north_america'
outPath = 'H:\\AddressIO_Home' # This should be where the full AddressIO data should be located (unzipped)
outGDB = r'H:\AddressIO_Home\workingGDB.gdb' #The GDB where the address range data is currently stored
stateURL = r'http://results.openaddresses.io/state.txt'
prjfile = r'H:\AddressIO_Scripts\PCS_Projection.prj' 
#------------------------------------------------------------------------------------------------------------------------------------
# function calls
t0 = time.time()
print('checking if state.txt url exists')
check_url_exists(stateURL)
stateRequest = requests.get(stateURL)
statetxt = os.path.join(outPath, 'state.txt')
print('Compiling State.txt info for analysis of new data')
print('Writing text to file')
with open(statetxt, 'wb') as txt:
    for line in urllib.request.urlopen(stateURL):
        txt.write(line)
stateDF = pd.read_csv(statetxt, sep='\t')
print('Calculating countryCode field')
stateDF['countryCode'] = stateDF.source.apply(lambda x: pd.Series(str(x).split('/')[0]))
stateDF = stateDF.loc[(stateDF.countryCode == 'ca') & (stateDF['address count'] >= 0)]
print('Creating dataset names from source field')
stateDF['locationName'] = stateDF.processed.apply(lambda x: pd.Series(str(x).split('/')[-1].split('.')[0]))
stateDF.rename(columns={'address count' : 'address_count'}, inplace=True)
# Build counts for the existing data and then
rows_to_download = [] # list of paths of zips to download
for row in stateDF.itertuples():
    if row.locationName == 'nan':
        continue
    prov = row.source.split('/')[1]
    # If file is not in current download of the addressIO data then download it as a new file
    if not os.path.exists(os.path.join(Old_Data, 'ca', prov, row.locationName + '.csv')) and row.processed != 'nan':
        rows_to_download.append(row.processed)
    if os.path.exists(os.path.join(Old_Data, 'ca', prov, row.locationName + '.csv')):
        oldProvdf = pd.read_csv(os.path.join(Old_Data, 'ca', prov, row.locationName + '.csv'))
        if len(oldProvdf) != row.address_count:
            print(f'{row.locationName} does not equal old count')
            print(f'Old Count: {len(oldProvdf)} New Count: {int(row.address_count)}')
            rows_to_download.append(row.processed)

# Download zips with files that need to be updated
intZips = [] # list of paths to intermediate zips
for zfile in rows_to_download:
    zipAllPathParts = splitall(zfile)
    if not os.path.exists(os.path.join(intermediateZipFolder, zipAllPathParts[-2])): # If prov sub directory does not exists create it
        os.makedirs(os.path.join(intermediateZipFolder, zipAllPathParts[-2])) # make prov sub directory for exported files
    print(f'Downloading: {os.path.split(zfile)[-1]}')
    r= requests.get(zfile, stream= True)
    downPath = os.path.join(intermediateZipFolder, zipAllPathParts[-2], zipAllPathParts[-1])
    if zipAllPathParts[-1] == 'province.zip':
        downPath = os.path.join(intermediateZipFolder, zipAllPathParts[-2], f'{zipAllPathParts[-2]}_{zipAllPathParts[-1]}')
    with open( downPath, 'wb') as fd:
        for chunk in r.iter_content(chunk_size= 128):
            fd.write(chunk)
    intZips.append(downPath)     

#Unzip the new csv's and add only the csv to the file structure
provstoupdate = [] # Track the provinces that need to be updated
for dlfile in intZips:
    with ZipFile(dlfile) as zipObj:
        for fileName in zipObj.namelist():
            if fileName.endswith('.csv'):
                allPathParts = splitall(fileName) # Splits path down to component parts
                print(f'Extracting: {fileName}')
                if allPathParts[-1] == 'province.csv': #get rid of repeated province name by adding prov code
                    print(f'province.csv renamed to {allPathParts[-2]}_{allPathParts[-1]}')
                    allPathParts[-1] = f'{allPathParts[-2]}_{allPathParts[-1]}'
                with zipObj.open(fileName) as zf, open(os.path.join(Old_Data, 'ca', allPathParts[-2], allPathParts[-1]), 'wb') as of:
                    shutil.copyfileobj(zf, of)
                if allPathParts[-2] not in provstoupdate:
                    provstoupdate.append(allPathParts[-2])
print(f' Number of location files updates: {len(rows_to_download)}')

provstoupdate = ['ab', 'bc', 'mb', 'nb', 'nl', 'ns', 'on', 'qc', 'sk', 'yt', 'pe', 'nt']
print('Province fcs to be updated:', provstoupdate)
for prov in provstoupdate:
    print('Updating:', prov)
    os.chdir(os.path.join(Old_Data, 'ca', prov))
    csvList = glob.glob(f'*.csv')
    print(f'Reading {len(csvList)} csv files into memory')
    dfFromEachFile = []
    fieldDtypes = {'ID' : 'object', 'NUMBER' : 'object'}
    for f in csvList:
        df = pd.read_csv(f, index_col= None, header=0, dtype= fieldDtypes)
        print(f)
        # sdf = pd.DataFrame.spatial.from_xy(df, x_column= 'LON', y_column= 'LAT')
        # sdf.spatial.to_featureclass(os.path.join(outGDB, prov, os.path.split(f)[1].split('.')[0].replace('-', '_')), overwrite= True)
        df['source'] = f
        dfFromEachFile.append(df)
    print('Concatonating all regional datasets')
    concatDF = pd.concat(dfFromEachFile, ignore_index= True)
    spatialConcatDF = pd.DataFrame.spatial.from_xy(concatDF, x_column= 'LON', y_column= 'LAT')
    #print('Reprojecting sdf into NAD83')
    #spatialConcatDF.spatial.project(spatial_reference= arcpy.SpatialReference('GCS_North_American_1983_CSRS'), transformation_name='NAD_1983_To_WGS_1984_1')
    print('Exporting full dataset')
    spatialConcatDF.spatial.to_featureclass(os.path.join(outGDB, f'{prov}_all_84'), overwrite= True)
    print(f'Reprojecting {prov}_all_84 to PCS_Lambert_Conformal_Conic')
    
# Converts all provincial/Territorial datasets into NGD projection
arcpy.env.workspace = outGDB
for fc in arcpy.ListFeatureClasses():
    if fc.endswith('_all_84'):
        print(f'Reprojecting {fc} to PCS_Lambert_Conformal_Conic')
        project_df = pd.DataFrame.spatial.from_featureclass(os.path.join(outGDB, f'{fc}'), sr= arcpy.SpatialReference(prjfile))
        project_df.spatial.to_featureclass(os.path.join(outGDB, f'{fc}_all'), overwrite= True)
        #arcpy.Delete_management(os.path.join(outGDB, f'{fc}'))

t1 = time.time() 
print(f'Total time taken to run script: {round((t1 - t0)/60, 2)} min')

print('DONE!')
