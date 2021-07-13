import io
import msoffcrypto
import csv
import openpyxl
import libnfs
import os
# use .env for store variables
from decouple import config

IP_NFS = config('IP_NFS')
SRC_PATH = config('SRC_PATH')
FILENAME = config('FILENAME')
GL_HEADER = ['hostname','ipaddr#project#owner#os#software','siemstatus']
TEMP_CSV = config('TEMP_CSV')

def get_inventory_nfs():
    ## Mount NFS.
    nfs = libnfs.NFS('nfs://'+ IP_NFS + '/mnt/nfs/' + SRC_PATH)
    ## Read file inventory and keep in bytearray format.
    file = nfs.open(FILENAME, mode='rb').read()
    ## Convert bytearray to BufferedReader for support msoffcrypto input type.
    fileobj = io.BytesIO(file)
    return fileobj


def decrypt_excel_password(excel_file):
    decrypted_workbook = io.BytesIO()
    with excel_file as file:
        office_file = msoffcrypto.OfficeFile(file)
        office_file.load_key(password=config('PASS_EX'))
        office_file.decrypt(decrypted_workbook)
    workbook = openpyxl.load_workbook(filename=decrypted_workbook)
    worksheet = workbook['Table1']
    return worksheet


def create_tmp_csv(sh):
    # os.remove(TEMP_CSV)
    # count=0
    with open(TEMP_CSV,'w') as out:
        c = csv.writer(out)
        for r in sh.rows:
            #count+=1
            #for i in r:
            #    print(i.value,count)
            c.writerow([cell.value for cell in r])
        out.close()

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
    sh = decrypt_excel_password(inventory)
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


if __name__ == '__main__':
    inventory = get_inventory_nfs()
    sh = decrypt_excel_password(inventory)
    create_tmp_csv(sh)
    final_list = read_tmp_csv()

    with open('result/final_out.csv','w') as file:
        writer = csv.DictWriter(file, fieldnames=GL_HEADER)
        writer.writeheader()
        for row in final_list:
            writer.writerow(row)