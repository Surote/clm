import io
import csv
import libnfs
import time
import sys
import os
# use .env for store variables
from decouple import config

IP_NFS = config('IP_NFS')
SRC_PATH = config('SRC_PATH')
DST_PATH = config('DST_PATH')
INPUT_FILENAME = config('INPUT_FILENAME')
OUTPUT_FILENAME = config('OUTPUT_FILENAME')
GL_HEADER = ['hostname','ipaddr#project#owner#os#software','siemstatus']
TEMP_CSV = config('TEMP_CSV')


def mount_nfs(foldermount):
    ## n = round of loop mount NFS
    n = 1
    interval_time = 5
    time_wait = 0
    ## time_limt = 30 mins
    time_limit = 1800
    while(time_wait <= time_limit):
        try:
            time.sleep(time_wait)
            nfs = libnfs.NFS('nfs://'+ IP_NFS + '/mnt/nfs/' + foldermount)
            return nfs
        except Exception as e:
            print(e)
            ## time_wait will increase if previous round not success
            time_wait = time_wait + (interval_time*n)
            n += 1
    return None


def access_nfs_file(nfs, operation, result=None):
    if(operation == 'read'):
        file = nfs.open(INPUT_FILENAME, mode='r').read()
    elif(operation == 'write' and result != None):
        file = nfs.open(OUTPUT_FILENAME, mode='w+').write(result)
    else:
        file = None
    return file


def get_inventory_nfs():
    ## Mount NFS.
    nfs = mount_nfs(SRC_PATH)
    if(nfs != None):
        ## Read file inventory and keep in bytearray format.
        file = access_nfs_file(nfs, 'read')
        return file
    else:
        print('Cannot Mount NFS for read.')


def reformat_inventory(csv_file):
    GL_DATA_LIST = []
    ##############################################################################################
    ## Use io.StringIO for provide a in-memory stream string if not use it the result will only ##
    ## get single character from line.                                                          ##
    ##############################################################################################
    reader = csv.DictReader(io.StringIO(csv_file))
    for row in reader:
        GL_INFO = init_dict()
        ## Skip line when host_id not exists.
        if row['host_id']:
            comb = row['oob_ip']+'#'+row['project_name_english']+'#'+row['operation_owner']+'#'\
                +row['os_name']+'#'+row['software_name']
            GL_INFO['hostname'] = row['host_name']
            GL_INFO['ipaddr#project#owner#os#software'] = comb
            GL_INFO['siemstatus'] = ''
            GL_DATA_LIST.append(GL_INFO)
            
    return GL_DATA_LIST


def init_dict():
    GL_INFO = { 'hostname':'',
            'ipaddr#project#owner#os#software':'',
            'siemstatus':''}
    return GL_INFO


def save_result_local(data):
    with open('result/final_out.csv','w') as file:
        writer = csv.DictWriter(file, fieldnames=GL_HEADER)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def save_result_nfs():
    ## Mount NFS.
    nfs = mount_nfs(DST_PATH)
    ## Open & Read Result file
    csv_file = open('result/final_out.csv', 'r')
    result = csv_file.read()
    if(nfs != None):
        ## Create File + Write File (Write function on NFS support only string)
        access_nfs_file(nfs, 'write', result)
    else:
        print('Cannot Mount NFS for write.')
    csv_file.close()

## For Flask
def get_start():
    inventory = get_inventory_nfs()
    if(inventory != None):
        ## Reformat for graylog
        final_list = reformat_inventory(inventory)

        ## Delete File before save new version due to flask save cache
        os.system('rm -rf result/final_out.csv')

        ## Create + Write File CSV in local
        save_result_local(final_list)

        ## Create + Write File CSV in NFS
        save_result_nfs()
        
        ## Create + Write File CSV in NFS
        save_result_nfs()
        return 'Done'
    else:
        return 'Something went wrong'


if __name__ == '__main__':
    inventory = get_inventory_nfs()
    if(inventory != None):
        ## Reformat for graylog
        final_list = reformat_inventory(inventory)

        ## Create + Write File CSV in local
        save_result_local(final_list)
        
        ## Create + Write File CSV in NFS
        save_result_nfs()