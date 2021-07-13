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


# def decrypt_excel_password(excel_file):
#     decrypted_workbook = io.BytesIO()
#     with excel_file as file:
#         office_file = msoffcrypto.OfficeFile(file)
#         office_file.load_key(password=config('PASS_EX'))
#         office_file.decrypt(decrypted_workbook)
#     workbook = openpyxl.load_workbook(filename=decrypted_workbook)
#     worksheet = workbook['Table1']
#     return worksheet

def reformat_inventory(csv_file):
    result = []
    ## Ex. Result csv_array =   ['5063', 'VRM01', '10.232.203.38', 
    ##                           'SILA1', 'Application', 'Euler 2.0', 
    ##                           'Huawei', '1903', 'New FM - Huawei Autin - Production', 
    ##                           'NIPAKORN SIANGZHEE', '', '', '', '', '', '', '\r']
    csv_array = (csv_file.split('\n'))
    for row in csv_array:
        result.append((row.split('\r'))[0].split(','))
    return result


# def create_tmp_csv(sh):
#     # os.remove(TEMP_CSV)
#     # count=0
#     with open(TEMP_CSV,'w') as out:
#         c = csv.writer(out)
#         for r in sh.rows:
#             #count+=1
#             #for i in r:
#             #    print(i.value,count)
#             c.writerow([cell.value for cell in r])
#         out.close()


def create_tmp_csv(sh):
    with open(TEMP_CSV,'w') as out:
        c = csv.writer(out)
        for r in sh:
            ## r[0] = host_id if host_id is empty string code will skip those line.
            if(r[0] != ''):
                c.writerow(r)


def init_dict():
    GL_INFO = { 'hostname':'',
            'ipaddr#project#owner#os#software':'',
            'siemstatus':''}
    return GL_INFO

    
def read_tmp_csv():
    GL_DATA_LIST = []
    with open(TEMP_CSV,'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            GL_INFO = init_dict()
            comb = row['oob_ip']+'#'+row['project_name_english']+'#'+row['operation_owner']+'#'+row['os_name']+'#'+row['software_name']
            GL_INFO['hostname'] = row['host_name']
            GL_INFO['ipaddr#project#owner#os#software'] = comb
            GL_INFO['siemstatus'] = ''
            GL_DATA_LIST.append(GL_INFO)
        file.close()
    # print(GL_DATA_LIST)
    return GL_DATA_LIST


def get_start():
    inventory = get_inventory_nfs()
    sh = reformat_inventory(inventory)
    create_tmp_csv(sh)
    final_list = read_tmp_csv()
    os.system('rm -rf result/final_out.csv')
    with open('result/final_out.csv','w') as file:
        writer = csv.DictWriter(file, fieldnames=GL_HEADER)
        writer.writeheader()
        for row in final_list:
            writer.writerow(row)
        file.close()
    return 'Done'


def upload_result_nfs():
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


if __name__ == '__main__':
    inventory = get_inventory_nfs()
    if(inventory != None):
        sh = reformat_inventory(inventory)
        create_tmp_csv(sh)
        final_list = read_tmp_csv()

        with open('result/final_out.csv','w') as file:
            writer = csv.DictWriter(file, fieldnames=GL_HEADER)
            writer.writeheader()
            for row in final_list:
                writer.writerow(row)
        
        ## Create + Write File CSV in NFS
        upload_result_nfs()