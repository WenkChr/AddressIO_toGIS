import os, sys, arcpy, requests, time
from zipfile import ZipFile
from io import BytesIO

# function definitions
def check_url_exists(url):
    import urllib3
    http = urllib3.PoolManager()
    request = http.request('GET', url)
    if request.status == 200:
        print('Website Exists')
        return 1
    else:
        print('Error with site.')
        print('Status Code: ' + str(request.status))
        return 0

def check_for_updates(url, old_data_zip):
    # Get Creation date for the old zip
    old_data_c_date = time.ctime(os.path.getctime(old_data_zip))
    # Get update date from online version
    # Explanation here: https://stackoverflow.com/questions/5710867/downloading-and-unzipping-a-zip-file-without-writing-to-disk

    
# constants
Data_GDB = 'H:\\AddressIO_Home\\workingGDB.gdb'
OpenIO_zip = "https://data.openaddresses.io/openaddr-collected-north_america.zip"
Old_Data_zip = 'H:\\AddressIO_Home\\openaddr-collected-north_america.zip'

# function calls
print('checking if url exists')
#check_url_exists(OpenIO_zip)
check_for_updates(OpenIO_zip, Old_Data_zip)
print('DONE!')