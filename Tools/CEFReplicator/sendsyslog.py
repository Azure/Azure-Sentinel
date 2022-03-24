#from distutils import extension
#from email import header
#from genericpath import exists
import json
import random
import csv
from syslog import Syslog, Level, Facility
import argparse
import multiprocessing
#from joblib import Parallel, delayed
#from tkinter import E
#from wsgiref.headers import Headers

# Building CEF
def build_cef_header(schemaSampledata):
    #print(schemaSampledata)
    cef_header_fields = ['name', 'deviceVendor', 'deviceProduct', 'signatureId', 'version', 'deviceVersion', 'severity']
    prefixes = {}
    #extensions = list(extensions)

    # Prepare CEF header
    prefixes['version'] = 1
    prefixes['deviceVendor'] = 'CEF Vendor'
    prefixes['deviceProduct'] = 'CEF Product'
    prefixes['deviceVersion'] = '1.0'
    prefixes['signatureId'] = '0'
    prefixes['name'] = 'CEF Event'
    prefixes['severity'] = 5  
    
    for field_name in cef_header_fields:
        try:
            prefixes[field_name] = random.choice(schemaSampledata["CEFHeader"][field_name]["values"])
        except (KeyError, TypeError):
            {}  

    return prefixes

def build_custom_extension(schemaSampledata,complete_header, extensions):
    # Prepare CEF Extensions
    #print(schemaSampledata, extensions)
    try:
        for field in complete_header:
            if field in schemaSampledata["customizations"].keys():
                extensions[field] =  ("{}={}".format(field, random.choice(schemaSampledata["customizations"][field]["values"])))       
        return extensions
    except  (KeyError, TypeError):
        return {'externalId': 'externalId=1499', 'lastActivityTime': 'lastActivityTime=2016-05-03 23:42:54+00', 'src': 'src=32.3.4.22.11', 'dst': 'dst=119.67.82.9', 'src_hostname': 'src_hostname=fortinet3242N', 'dst_hostname': 'dst_hostname=google.com', 'src_username': 'src_username=hjrkd', 'dst_username': 'dst_username=dkedd', 'dst_email_id': 'dst_email_id=jkss@hfjfk.com', 'startTime': 'startTime=2019-05-03 23:42:54+00', 'url': 'url="http://greatfilesarey.asia/QA/files_to_pcaps/74280968a4917da52b5555351eeda969.bin http://greatfilesarey.asia/QA/files_to_pcaps/1813791bcecf3a3af699337723a30882.bin"', 'fileHash': 'fileHash=bce00351cfc559afec5beb90ea387b03788e4af5', 'fileType': 'fileType=PE32', 'malwareCategory': 'malwareCategory=Trojan_Generic', 'malwareSeverity': 'malwareSeverity=0.87', 'dst_country': 'dst_country=Nepal'}  
    
# Post to Syslog

def post_syslog(msg, hostname):
    print(msg)
    log = Syslog(host=hostname)
    log.send(msg,Level.INFO)



#print (random.choice(schemaSampledata["CEFHeader"]["name"]["values"]))

# Read header from sample data
def read_header_sampledata(filename):
    try:
        with open(filename, 'r') as csv_file:
            lines = csv_file.readlines()
            headers = [i.strip() for i in lines[0].split(',')]
        return headers
    except OSError as e:
        print("Make sure file exists with at least header, taking default header",e.errno)
        return ['externalId', 'lastActivityTime', 'src', 'dst', 'src_hostname', 'dst_hostname', 'src_username', 'dst_username', 'dst_email_id', 'startTime', 'url', 'fileHash', 'fileType', 'malwareCategory', 'malwareSeverity', 'dst_country']
    


def get_kv_pairs(headers, record):
    extensions1 = {}
    values = [i.strip() for i in record.split(',')]
    for i,field in enumerate(headers):
        extensions1[field] =  ("{}={}".format(headers[i],values[i]))
    return extensions1

def syslog_message_format(args,schemaSampledata,extenstion_data):
    if str(args.eventtype).lower() == 'cef':
        template = 'CEF:{version}|{deviceVendor}|{deviceProduct}|{deviceVersion}|{signatureId}|{name}|{severity}|{extenstion_data}'    
        prefixes = build_cef_header(schemaSampledata)
        return_message = template.format(extenstion_data=' '.join(extenstion_data.values()), **prefixes)
    elif str(args.eventtype).lower() == 'syslog':
        template = 'CEF:{version}|{deviceVendor}|{deviceProduct}|{deviceVersion}|{signatureId}|{name}|{severity}|{extenstion_data}'    
        prefixes = build_cef_header(schemaSampledata)
        return_message = template.format(extenstion_data=' '.join(extenstion_data.values()), **prefixes)
    
    post_syslog(return_message, hostname=args.host) 

def build_message(args, headers):
    try:
        with open(args.input_file, 'r') as csv_file:
            lines = csv_file.readlines()
            if len(lines) > 1:
                for record in lines[1:]:
                    extenstion_data = get_kv_pairs(headers,record.strip())
                    if schemaSampledata != "NULL":
                        extenstion_data = build_custom_extension(schemaSampledata,complete_header=headers, extensions=extenstion_data)
                    syslog_message_format(args,schemaSampledata,extenstion_data)
            else:
                extenstion_data = build_custom_extension(schemaSampledata,complete_header=headers, extensions={})
                syslog_message_format(args,schemaSampledata,extenstion_data)
            
            #print (extenstion_data)
    except OSError as e:
        print("Make sure input file exists with the header and try again. For now taking default sample event")
        extenstion_data = build_custom_extension(schemaSampledata, complete_header=headers, extensions={})
        syslog_message_format(args,schemaSampledata,extenstion_data)



#print("{extensions}".format(extensions=' '.join(extensions.values())))


# Building Syslog




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Syslog and CEF builder and replayer')
    parser.add_argument('input_file', metavar='DEFINITION_FILE', type=str, help='file containing sample events')
    parser.add_argument('--cust_file', metavar='EVENT_CUSTOMIZATIONS_FILE', type=str, default="None", help='Customizations defined here')
    parser.add_argument('--host', type=str, help='Syslog destination address')
    parser.add_argument('--port', type=int, default=514, help='Syslog destination port')
    parser.add_argument('--eventtype', type=str, default='CEF', help='CEF or Syslog')
    parser.add_argument('--eps', type=int, default=100, help='Max EPS')

    args = parser.parse_args()
    #'C:\\Repositories\\Anki-Playground\\cefevent\\SampleData.csv'
    print (args.input_file)
    schemaSampledata = "NULL"

    headers = read_header_sampledata(args.input_file)

    try:
        if args.cust_file != "None":
            with open(args.cust_file, 'r') as json_file:
                schemaSampledata = json.load(json_file)
        else:
            print("No customization requirements provided. Skipping customizations")
    except OSError as e:
        print("Make sure input file exists with the required customizations and try again {}",e.errno)

    pool_obj = multiprocessing.Pool()
    

    for i in range(1,args.eps):
        build_message(args, headers)
  
    
    #print (extenstion_data)

   

   #168.61.69.216