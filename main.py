from decouple import config
import msoffcrypto
import openpyxl
import libnfs
import csv
import io


## Edit variable Here ##
IP_NFS = config('IP_NFS')
SRC_PATH = config('SRC_PATH')
DST_PATH = config('DST_PATH')
FILENAME = config('FILENAME')
GL_HEADER = ['hostname','ipaddr#project#owner#os#software','siemstatus']
GL_DATA_LIST = []
TEMP_CSV = 'temp.csv'


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
    with open(TEMP_CSV,'w') as out:
        c = csv.writer(out)
        for r in sh.rows:
            c.writerow([cell.value for cell in r])


def init_dict():
    GL_INFO = { 'hostname':'',
            'ipaddr#project#owner#os#software':'',
            'siemstatus':''}
    return GL_INFO

    
def read_tmp_csv():
    with open(TEMP_CSV,'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            GL_INFO = init_dict()
            comb = row['oob_ip']+'#'+row['project_name_english']+'#'+row['operation_owner']+'#'+row['os_name']+'#'+row['software_name']
            GL_INFO['hostname'] = row['host_name']
            GL_INFO['ipaddr#project#owner#os#software'] = comb
            GL_INFO['siemstatus'] = ''
            GL_DATA_LIST.append(GL_INFO)
    # print(GL_DATA_LIST)
    return GL_DATA_LIST


def upload_result_nfs():
    ## Mount NFS.
    nfs = libnfs.NFS('nfs://'+ IP_NFS + '/mnt/nfs/' + DST_PATH)
    ## Open & Read Result file
    csv_file = open('final_out.csv', 'r')
    result = csv_file.read()
    ## Create File + Write File (Write function on NFS support only string)
    nfs.open('/final_out.csv', mode='w+').write(result)
    csv_file.close()


if __name__ == '__main__':
    ## Get File Inventory from NFS
    inventory = get_inventory_nfs()
    sh = decrypt_excel_password(inventory)
    create_tmp_csv(sh)
    final_list = read_tmp_csv()

    with open('final_out.csv','w') as file:
        writer = csv.DictWriter(file, fieldnames=GL_HEADER)
        writer.writeheader()
        for row in final_list:
            writer.writerow(row)
    
    ## Create + Write File CSV in NFS
    upload_result_nfs()