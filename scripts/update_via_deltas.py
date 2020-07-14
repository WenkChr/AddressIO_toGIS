import os, sys,  requests, time, urllib
import pandas as pd
from zipfile import ZipFile


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
stateURL = r'http://results.openaddresses.io/state.txt'
#------------------------------------------------------------------------------------------------------------------------------------
# function calls
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
    print(f'Downloading: {os.path.split(zfile)[-1]}')
    urlSplit = os.path.split(zfile)
    r= requests.get(zfile, stream= True)
    downPath = os.path.join(outPath, 'IntermediateZips', os.path.split(zfile)[-1])
    with open( downPath, 'wb') as fd:
        for chunk in r.iter_content(chunk_size= 128):
            fd.write(chunk)
    intZips.append(downPath)     


print(len(rows_to_download))
print(rows_to_download)

print('DONE!')
