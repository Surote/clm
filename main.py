import io
import msoffcrypto
import csv
import openpyxl
import libnfs

FILENAME = '/hava_inventory_v2.xlsx'
GL_HEADER = ['hostname','ipaddr#project#owner#os#software','siemstatus']
GL_DATA_LIST = []
TEMP_CSV = 'temp.csv'


def get_excel_nfs():
    nfs = libnfs.NFS('nfs://172.16.22.155/mnt/nfs/source-inventory-hava/')
    file = nfs.open(FILENAME, mode='rb').read()
    fileobj = io.BytesIO(file)
    return fileobj


def decrypt_excel_password(excel_file):
    decrypted_workbook = io.BytesIO()
    with excel_file as file:
        office_file = msoffcrypto.OfficeFile(file)
        office_file.load_key(password='clm@1234')
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
    print(GL_DATA_LIST)
    return GL_DATA_LIST


if __name__ == '__main__':
    excel_file = get_excel_nfs()
    sh = decrypt_excel_password(excel_file)
    create_tmp_csv(sh)
    final_list = read_tmp_csv()

    with open('final_out.csv','w') as file:
        writer = csv.DictWriter(file, fieldnames=GL_HEADER)
        writer.writeheader()
        for row in final_list:
            writer.writerow(row)