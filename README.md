# AddressIO_toGIS

This project takes the csv data from https://openaddresses.io/ which provides a large worldwide open source dataset of address points taken from authoritative sources. More documentation on the project can be found here: https://github.com/openaddresses/openaddresses/blob/master/README.md 

This project takes the data for Canada and creates several products from it in a file geodatabase:
    1.) A feature dataset with all csv's for the given province contained within it
    2.) A master province address file with all individual files merged. In order to link back to the source csv a 'source' field is calculated as part of this process
    3.) A polygon feature class is created to show the Census Sub Divisions (CSD) (2016 vintage) in which the adresses are located as well as a count of those addresses that occur for each CSD

This project was created with continuous updates in mind. The Initial_csv_to_fc.py script will download and organize the enitre dataset while the update_via_deltas dataset will check for updates and changes to the address counts for each of the inividual csv's. If there is a difference between the new count and the old count then that csv is downloaded and all associated products are updates to reflect the changes.

To ensure variable continuity between script before running the scripts you should create a file called 'environments.env' which should be formatted as below but changed to reflect your workspace:

'''
#Base out directory
OUT_DIR= H:\\AddressIO_Home 

# Initial Setup vars
START_PATH = ${OUT_DIR}/openaddr-collected-north_america/ca
PROVS = ['bc', 'ab', 'sk', 'mb', 'on', 'qc', 'nb', 'ns', 'nl', 'nt', 'pe', 'yt', 'nu']
IO_ESS_FIELDS = ['OBJECTID', 'LAT', 'LON', 'NUMBER', 'STREET', 'UNIT', 'CITY', 'POSTCODE', 'SOURCE']
PRJ_FILE = H:\\AddressIO_Scripts\\PCS_Projection.prj
SOURCE_ZIP = 'https://data.openaddresses.io/openaddr-collected-north_america.zip' 

# update_via_deltas.py vars
INT_ZIP_DIR = ${OUT_DIR}/IntermediateZips
OLD_DATA = ${OUT_DIR}\openaddr-collected-north_america
OUT_GDB = ${OUT_DIR}/workingGDB.gdb
STATE_URL = http://results.openaddresses.io/state.txt

#Coverage Creation Vars
CSD_PATH = ${OUT_DIR}/lcsd000b16a_e.shp
SCRATCH_GDB = ${OUT_DIR}/scratch.gdb
'''