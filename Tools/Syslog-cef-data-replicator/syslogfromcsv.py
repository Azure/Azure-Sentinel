#from distutils import extension
#from email import header
#from genericpath import exists
import json
import random
#from syslog import Syslog, Level, Facility
import argparse
import datetime
import time
import socket
from multiprocessing import Process
from threading import Thread as worker



class Facility:
  "Syslog facilities"
  KERN, USER, MAIL, DAEMON, AUTH, SYSLOG, \
  LPR, NEWS, UUCP, CRON, AUTHPRIV, FTP = range(12)

  LOCAL0, LOCAL1, LOCAL2, LOCAL3, \
  LOCAL4, LOCAL5, LOCAL6, LOCAL7 = range(16, 24)

class Level:
  "Syslog levels"
  EMERG, ALERT, CRIT, ERR, \
  WARNING, NOTICE, INFO, DEBUG = range(8)

class Syslog:
  """A syslog client that logs to a remote server.

  Example:
  >>> log = Syslog(host="foobar.example")
  >>> log.send("hello", Level.WARNING)
  """
  def __init__(self,
               host="localhost",
               port=514,
               facility=Facility.DAEMON,
               protocol='TCP'):
    self.host = host
    self.port = port
    self.facility = facility
    self.protocol = protocol
    if self.protocol == 'UDP':
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    elif self.protocol == 'TCP':
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
    else:
        raise Exception('Invalid protocol {}, valid options are UDP and TCP'.format(self.protocol))

  def send(self, message, level=Level.NOTICE):
    "Send a syslog message to remote host using UDP or TCP"
    data = "<%d>%s" % (level + self.facility*8, message)
    if self.protocol == 'UDP':
        self.socket.sendto(data.encode('utf-8'), (self.host, self.port))
    else:
        self.socket.send(data.encode('utf-8'))

  def warn(self, message):
    "Send a syslog warning message."
    self.send(message, Level.WARNING)

  def notice(self, message):
    "Send a syslog notice message."
    self.send(message, Level.NOTICE)

  def error(self, message):
    "Send a syslog error message."
    self.send(message, Level.ERR)


def build_custom_extension(schemaSampledata,complete_header, extensions):
    # Prepare CEF Extensions
    # print(schemaSampledata, extensions)
    try:
        for field in complete_header:
            if field in schemaSampledata["customizations"].keys():
                #print (schemaSampledata["customizations"][field]["values"])
                if schemaSampledata["customizations"][field]["data_type"] == "datetime" and schemaSampledata["customizations"][field]["values"] == ["current"]:
                    if schemaSampledata["customizations"][field]["format"] == "epoch":
                        val = datetime.datetime.utcnow().timestamp()
                    elif schemaSampledata["customizations"][field]["format"] == "epochmilliseconds": 
                        val = datetime.datetime.utcnow().timestamp() * 1000
                    else:   
                        val = datetime.datetime.utcnow().strftime(schemaSampledata["customizations"][field]["format"])
                    extensions[field] =  ("{}{}{}".format(field, KVDelimiter, val ))
                else:
                    extensions[field] =  ("{}{}{}".format(field, KVDelimiter, random.choice(schemaSampledata["customizations"][field]["values"])))       
        return extensions
    except  (KeyError, TypeError):
        return {'version': 'version=0', 'deviceVendor': 'deviceVendor=Fortinet', 'deviceProduct': 'deviceProduct=Fortigate', 'deviceVersion': 'deviceVersion=19', 'signatureId': 'signatureId=3.5.4.3', 'name': 'name=Phishing', 'severity': 'severity=4', 'externalId': 'externalId=1499', 'lastActivityTime': 'lastActivityTime=2016-05-03 23:42:54+00', 'src': 'src=32.3.4.22.11', 'dst': 'dst=119.67.82.9', 'src_hostname': 'src_hostname=fortinet3242N', 'dst_hostname': 'dst_hostname=google.com', 'src_username': 'src_username=hjrkd', 'dst_username': 'dst_username=dkedd', 'dst_email_id': 'dst_email_id=jkss@hfjfk.com', 'startTime': 'startTime=2019-05-03 23:42:54+00', 'url': 'url=http://greatfilesarey.asia/QA/files_to_pcaps/74280968a4917da52b5555351eeda969.bin http://greatfilesarey.asia/QA/files_to_pcaps/1813791bcecf3a3af699337723a30882.bin', 'fileHash': 'fileHash=bce00351cfc559afec5beb90ea387b03788e4af5', 'fileType': 'fileType=PE32', 'malwareCategory': 'malwareCategory=Trojan_Generic', 'malwareSeverity': 'malwareSeverity=0.87', 'dst_country': 'dst_country=SLNK'}

def post_syslog(msg, hostname):
    #print(msg)
    log = Syslog(host=hostname)
    log.send(msg,Level.INFO)



#print (random.choice(schemaSampledata["CEFHeader"]["name"]["values"]))

# Read header from sample data
def read_csv_header_sampledata(filename):
    try:
        with open(filename, 'r', encoding="utf8") as csv_file:
            lines = csv_file.readlines()
            headers = [i.strip() for i in lines[0].split(',')]
        return headers
    except OSError as e:
        print("Make sure file exists with at least header, taking default header",e)
        return ['externalId', 'lastActivityTime', 'src', 'dst', 'src_hostname', 'dst_hostname', 'src_username', 'dst_username', 'dst_email_id', 'startTime', 'url', 'fileHash', 'fileType', 'malwareCategory', 'malwareSeverity', 'dst_country']
    


def get_kv_pairs_csv(headers, record):
    extensions1 = {}   
    values = [i.strip() for i in record.split(',')]
    #headers_ext = [i for i in headers if i not in cef_header_fields]
    for i,field in enumerate(headers):
        #if not(field in cef_header_fields): 
        extensions1[field] =  ("{}{}{}".format(headers[i],KVDelimiter,values[i]))
    return extensions1



def syslog_message_format(args,schemaSampledata,extenstion_data):
    return_message = ""
    try:
        if str(args.eventtype).lower() == 'cef':
            cef_header = {}
            cef_ext = {}
            template = 'CEF:{version}|{deviceVendor}|{deviceProduct}|{deviceVersion}|{signatureId}|{name}|{severity}|{extenstion_data}' 
            cef_header_fields = ['name', 'deviceVendor', 'deviceProduct', 'signatureId', 'version', 'deviceVersion', 'severity']
            cef_header_fields_dummy = {'version': '0', 'deviceVendor': 'CEF Vendor','deviceProduct': 'CEF Product','deviceVersion': 'CEF Version','signatureId': 'CEF Sig','name': 'CEF Attack Name','severity': 'CEF SEV'} 
            for field in cef_header_fields:
                if field in extenstion_data:
                    cef_header[field] = extenstion_data[field].split("=")[1]
                else:
                    cef_header[field] = cef_header_fields_dummy[field]
            
            for field in extenstion_data:
                if not(field in cef_header_fields):
                    cef_ext[field] = extenstion_data[field]          
            #print(cef_header)
            prefixes = cef_header
            return_message = template.format(extenstion_data=' '.join(cef_ext.values()), **prefixes)
        elif str(args.eventtype).lower() == 'syslog':
            #print("HEEEEEEEEEEEEEEEEEEEEREEEEEEEEEEEEEEEE")
            syslog_header = {}
            syslog_ext = {}
            #template = '<{priority}>{version} {ISOTimeStamp} {hostName} {application} {pid} {messageId} {structured_data} {message}'
            template = schemaSampledata["SyslogMessage"]["syslog_message_template"]["values"]
            syslog_header_fields =  schemaSampledata["SyslogMessage"]["syslog_header_fields"]["values"]
            KVDelimiter = schemaSampledata["SyslogMessage"]["KVDelimiter"]["values"]
            fieldDelimiter = schemaSampledata["SyslogMessage"]["fieldDelimiter"]["values"]
            syslog_header_fields_dummy = {'priority': '139', 'version': '1','ISOTimeStamp': '2022-03-31 11:59:59','hostName': 'SYSLOG_Host','application': 'SYSLOG_App', 'pid': 'process','messageId': '1234'} 
            #print(extenstion_data)
            for field in syslog_header_fields:
                if field in extenstion_data:
                    syslog_header[field] = extenstion_data[field].split(KVDelimiter)[1]
                else:
                    syslog_header[field] = syslog_header_fields_dummy[field]
            #print(syslog_header)
            for field in extenstion_data:
                if not(field in syslog_header_fields):
                    syslog_ext[field] = extenstion_data[field]          
            #print(syslog_ext)
            prefixes = syslog_header
            return_message = template.format(structured_data=fieldDelimiter.join(syslog_ext.values()),message='', **prefixes)
        post_syslog(return_message, hostname=args.host) 
    except  Exception as e:
        print(" syslog_message_format Exception {}",str(e))    
    

def build_message_csv(args, headers):
    #print ("I am here")
    try:
        with open(args.input_file, 'r', encoding="utf8") as csv_file:
            lines = csv_file.readlines()
            if len(lines) > 1:
                for record in lines[1:]:
                    extenstion_data = get_kv_pairs_csv(headers,record.strip())
                    #print(extenstion_data)
                    #cef_header = get_cef_header(headers,record.strip())
                    #print(cef_header)
                    if schemaSampledata != "NULL":
                        #print("HEEEEEEEEEEEEEEEE")
                        extenstion_data = build_custom_extension(schemaSampledata,complete_header=headers, extensions=extenstion_data)
                        #cef_header = get_cef_header(headers,record.strip())
                        #print (extenstion_data)
                    syslog_message_format(args,schemaSampledata,extenstion_data)
            else:
                extenstion_data = build_custom_extension(schemaSampledata,complete_header=headers, extensions={})
                syslog_message_format(args,schemaSampledata,extenstion_data)
            
            #print (extenstion_data)
    except OSError as e:
        print("Make sure input file exists with the header and try again. For now taking default sample event")
        extenstion_data = build_custom_extension(schemaSampledata, complete_header=headers, extensions={})
        syslog_message_format(args,schemaSampledata,extenstion_data)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Syslog and CEF builder and replayer')
    parser.add_argument('input_file', metavar='DEFINITION_FILE', type=str, help='file containing sample events')
    parser.add_argument('--cust_file', metavar='EVENT_CUSTOMIZATIONS_FILE', type=str, default="None", help='Customizations defined here')
    parser.add_argument('--host', type=str, default='localhost', help='Syslog destination address')
    parser.add_argument('--port', type=int, default=514, help='Syslog destination port')
    parser.add_argument('--eventtype', type=str, default='CEF', help='CEF or Syslog')
    parser.add_argument('--eventcount', type=int, default=200, help='Max events')

    args = parser.parse_args()
    
    """
    #args = []
    input_file = "C:\\Repositories\\Anki-Playground\\CEFReplicator\\syslog_meraki_raw.log"
    cust_file = "fortigate_customizations.json"
    host = "138.91.95.213"
    port = 514
    eventtype = "CEF"
    fileformat = "kvpair"
    eventcount = 100
    """
    schemaSampledata = "NULL"
    headers = read_csv_header_sampledata(args.input_file)

    try:
        if args.cust_file != "None":
            with open(args.cust_file, 'r') as json_file:
                schemaSampledata = json.load(json_file)
        else:
            print("No customization requirements provided. Skipping customizations")
    except OSError as e:
        print("Make sure input file exists with the required customizations and try again {}",e.errno)

    try:
        KVDelimiter = schemaSampledata["SyslogMessage"]["KVDelimiter"]["values"]
    except KeyError:
        KVDelimiter = "="
        print("Customization vaules not available takig default")  
    
    #print(schemaSampledata)

    if args.eventtype != 'syslog':
        KVDelimiter = "="
    
    now = datetime.datetime.now()
    

    for i in range(1,100000000000000000000):
        time_diff = (datetime.datetime.now() - now).total_seconds()
        eps = i / (time_diff if time_diff > 0 else 1)
        if eps > args.eventcount:
            time.sleep(1)
            #now = datetime.datetime.now()
        else:
            #build_message_csv(args,headers)
            p = worker(target=build_message_csv, args=(args,headers))
            p.start()
            p.join() 
        print ("Sent {} messages till  with eps {} ".format(i,eps))
    """
    for i in range(1,args.eventcount):
        p = worker(target=build_message_csv, args=(args,headers))
        p.start()
        p.join()  
    """
    #print (extenstion_data)
    #168.61.69.216