import sys, os, arcpy

arcpy.env.overwriteOutput = True

# Functions

def delete_non_essential_fields(fc, essential_fields):
    if isinstance(essential_fields, (list, tuple)):
        for f in arcpy.ListFields(fc):
            if f.name not in essential_fields and not f.required:
                arcpy.DeleteField_management(fc, f.name)
     
def buildGDB(outPath, gdb_name, feature_datasets=[], spatial_ref = arcpy.SpatialReference('WGS 1984')):
    # Creates a gdb from inputs and adds in feature datasets to that gdb if any and returns the path to the gdb
    gdb_path = os.path.join(outPath, gdb_name + '.gdb')
    if arcpy.Exists(gdb_path):
        return gdb_path
    arcpy.CreateFileGDB_management(outPath, gdb_name)
    if isinstance(feature_datasets, list) and len(feature_datasets) > 0:
        for fds in feature_datasets:
            arcpy.CreateFeatureDataset_management(gdb_path, fds, spatial_ref)

    return gdb_path

def batch_csv_to_fc(start_path, outGDB, x, y):
    
    def csv_to_fc(csv, outGDB, out_name, x, y):
        out_fc = os.path.join(outGDB, out_name)
        if arcpy.Exists(out_fc):
            print('File already exists moving onto next one')
            return out_fc 
        table = arcpy.TableToTable_conversion(csv, os.path.split(outGDB)[0], out_name + '_table')
        xyl = arcpy.MakeXYEventLayer_management(table, x, y, 'xyl')
        arcpy.FeatureClassToFeatureClass_conversion(xyl, outGDB, out_name)
        arcpy.Delete_management(table)
        return out_fc
    
    # dict for all fc's sorted by province into a specific list
    prov_files = {'bc':[], 'ab': [], 'sk':[], 'mb':[], 'on':[], 'qc':[], 'nb':[], 'ns':[], 'nl':[], 'nt':[], 'pe':[],
                'yt':[], 'nu':[]}
    for root, dirs, files in os.walk(start_path):
        for f in files:
            if '.csv' in f:
                print('Converting ' + f + ' to a fc')
                f_path = os.path.join(root, f)
                fc_name = f.split('.')[0]
                prov_abbv = root.split('\\')[-1]
                if '-' in fc_name:
                    fc_name = fc_name.replace('-', '_')
                if fc_name == 'province':
                    fc_name =  prov_abbv + '_province'
                out_location = os.path.join(outGDB, prov_abbv) 
                current_fc = csv_to_fc(f_path, out_location, fc_name, x, y)
                prov_files[prov_abbv].append(current_fc) 
                arcpy.AddField_management( current_fc, 'SOURCE', 'TEXT')
                arcpy.CalculateField_management(current_fc, 'SOURCE', expression= "'" + f + "'", expression_type= 'PYTHON3')
    
def merge_all_in_fds(path_to_gdb, outGDB, common_essential_fields,
                    provs = ['bc', 'ab', 'sk', 'mb', 'on', 'qc', 'nb', 'ns', 'nl', 'nt', 'pe', 'yt', 'nu']):
    
    print('Merging all files by province')
    for prov in provs:
        print('Merging all files for: ' + prov )
        arcpy.env.workspace = os.path.join(outGDB, prov)
        fc_files = arcpy.ListFeatureClasses()
        fc_files_w_path = [os.path.join(outGDB, prov, f) for f in fc_files]
        
        for f in fc_files_w_path: delete_non_essential_fields(f, common_essential_fields)
        
        arcpy.Merge_management(fc_files_w_path, os.path.join(outGDB, prov + '_all'))

# Constants
spatial_ref = arcpy.SpatialReference('WGS 1984')
sourceZip = r'https://data.openaddresses.io/openaddr-collected-north_america.zip'
out_path = 'H:\\AddressIO_Home'
start_path = r'H:\AddressIO_Home\openaddr-collected-north_america\ca'
provs = ['bc', 'ab', 'sk', 'mb', 'on', 'qc', 'nb', 'ns', 'nl', 'nt', 'pe', 'yt', 'nu']
IO_essential_fields = ['OBJECTID', 'LAT', 'LON', 'NUMBER', 'STREET', 'UNIT', 'CITY', 'POSTCODE', 'SOURCE']
# Calls
working_gdb = buildGDB(out_path, 'workingGDB', feature_datasets= provs)
#batch_csv_to_fc(start_path, working_gdb, 'LON', 'LAT')
merge_all_in_fds(working_gdb, working_gdb, common_essential_fields= IO_essential_fields)

print('DONE!')
