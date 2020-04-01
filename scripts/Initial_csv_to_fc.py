import sys, os, arcpy, requests

arcpy.env.overwriteOutput = True
# Functions

def batch_csv_to_fc(start_path, outGDB, x, y):
    
    def csv_to_fc(csv, outGDB, out_name, x, y):
        table = arcpy.TableToTable_conversion(csv, outGDB, out_name + '_table')
        xyl = arcpy.MakeXYEventLayer_management(table, x, y, 'xyl')
        arcpy.FeatureClassToFeatureClass_conversion(xyl, outGDB, out_name)
        arcpy.Delete_management(table)

    for root, dirs, files in os.walk(start_path):
        for f in files:
            if '.csv' in f:
                print('Converting ' + f + ' to a fc')
                f_path = os.path.join(root, f)
                fc_name = f.split('.')[0]
                if '-' in fc_name:
                    fc_name = fc_name.replace('-', '_')
                if fc_name == 'province':
                    fc_name = root.split('\\')[-1] + '_province'

                csv_to_fc(f_path, outGDB, fc_name, x, y)
                current_fc = os.path.join(outGDB, fc_name)
                arcpy.AddField_management( current_fc, 'SOURCE', 'TEXT')
                arcpy.CalculateField_management(current_fc, 'SOURCE', )

def DeltaUpdater():
    pass

# Constants

sourceZip = r'https://data.openaddresses.io/openaddr-collected-north_america.zip'
out_path = 'H:\\AddressIO_Home'
start_path = r'H:\AddressIO_Home\openaddr-collected-north_america\ca'
working_gdb = arcpy.CreateFileGDB_management(out_path, 'workingGDB')
# Calls
batch_csv_to_fc(start_path, working_gdb, 'LON', 'LAT')
DeltaUpdater()

print('DONE!')
