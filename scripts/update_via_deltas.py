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

def check_for_updates(url, old_data_zip):
    # Get Creation date for the old zip
    old_data_c_date = time.ctime(os.path.getctime(old_data_zip))
    # Get update date from online version
    # Explanation here: https://stackoverflow.com/questions/5710867/downloading-and-unzipping-a-zip-file-without-writing-to-disk
#--------------------------------------------------------------------------------------------------------------------------------
# inputs
Data_GDB = 'H:\\AddressIO_Home\\workingGDB.gdb'
OpenIO_zip = "https://data.openaddresses.io/openaddr-collected-north_america.zip"
Old_Data_zip = 'H:\\AddressIO_Home\\openaddr-collected-north_america.zip'
outPath = 'H:\\AddressIO_Scripts'
stateURL = r'http://results.openaddresses.io/state.txt'
#------------------------------------------------------------------------------------------------------------------------------------
# function calls
print('checking if state.txt url exists')
check_url_exists(stateURL)
stateRequest = requests.get(stateURL)
statetxt = os.path.join(outPath, 'state.txt')
print('Writing text to file')
with open(statetxt, 'wb') as txt:
    for line in urllib.request.urlopen(stateURL):
        txt.write(line)
stateDF = pd.read_csv(statetxt, sep='\t')

stateFields = ['source','cache','sample','geometry', 'type', 'address count', 'version', 'fingerprint', 'cache time', 'processed', 
                'process time', 'process hash', 'output', 'attribution required', 'attribution name', 'share-alike', 'code version']
#stateDF = pd.read_csv(statetxt, sep='delimiter', engine='python', header=None)

print(stateDF.head())

print('DONE!')
