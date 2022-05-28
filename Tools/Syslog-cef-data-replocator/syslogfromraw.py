#from distutils import extension
#from email import header
#from genericpath import exists
#from datetime import datetime
#from fileinput import filename
#from importlib.metadata import files
import json
import random
import csv
#from syslog import Syslog, Level, Facility
import argparse
import re
import datetime
from threading import Thread as worker
from logging.handlers import SysLogHandler
import logging
import pycef
import pysyslog
import shlex
import time
import socket
#from joblib import Parallel, delayed
#from tkinter import E
#from wsgiref.headers import Headers

# Building CEF
"""
def build_cef_header_csv(args,schemaSampledata):
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
"""


def build_custom_extension_for_raw(schemaSampledata,complete_header, extensions):
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
                    extensions[field] =  val
                else:
                    extensions[field] =  random.choice(schemaSampledata["customizations"][field]["values"])
                    #print(extensions[field])      
        return extensions
    except  (KeyError, TypeError):
        return {'version': 'version=0', 'deviceVendor': 'deviceVendor=Fortinet', 'deviceProduct': 'deviceProduct=Fortigate', 'deviceVersion': 'deviceVersion=19', 'signatureId': 'signatureId=3.5.4.3', 'name': 'name=Phishing', 'severity': 'severity=4', 'externalId': 'externalId=1499', 'lastActivityTime': 'lastActivityTime=2016-05-03 23:42:54+00', 'src': 'src=32.3.4.22.11', 'dst': 'dst=119.67.82.9', 'src_hostname': 'src_hostname=fortinet3242N', 'dst_hostname': 'dst_hostname=google.com', 'src_username': 'src_username=hjrkd', 'dst_username': 'dst_username=dkedd', 'dst_email_id': 'dst_email_id=jkss@hfjfk.com', 'startTime': 'startTime=2019-05-03 23:42:54+00', 'url': 'url=http://greatfilesarey.asia/QA/files_to_pcaps/74280968a4917da52b5555351eeda969.bin http://greatfilesarey.asia/QA/files_to_pcaps/1813791bcecf3a3af699337723a30882.bin', 'fileHash': 'fileHash=bce00351cfc559afec5beb90ea387b03788e4af5', 'fileType': 'fileType=PE32', 'malwareCategory': 'malwareCategory=Trojan_Generic', 'malwareSeverity': 'malwareSeverity=0.87', 'dst_country': 'dst_country=SLNK'}
{'version': 'version=0', 'deviceVendor': 'deviceVendor=JUNIPER', 'deviceProduct': 'deviceProduct=Cortex', 'deviceVersion': 'deviceVersion=19', 'signatureId': 'signatureId=1.89.12.3', 'name': 'name=TROJAN_GIPPERS.DC', 'severity': 'severity=6', 'externalId': 'externalId=1499', 'lastActivityTime': 'lastActivityTime=2016-05-03 23:42:54+00', 'src': 'src=101.21.21.1', 'dst': 'dst=201.32.13.56', 'src_hostname': 'src_hostname=fortinet3242N', 'dst_hostname': 'dst_hostname=google.com', 'src_username': 'src_username=hjrkd', 'dst_username': 'dst_username=dkedd', 'dst_email_id': 'dst_email_id=jkss@hfjfk.com', 'startTime': 'startTime=2019-05-03 23:42:54+00', 'url': 'url=http://greatfilesarey.asia/QA/files_to_pcaps/74280968a4917da52b5555351eeda969.bin http://greatfilesarey.asia/QA/files_to_pcaps/1813791bcecf3a3af699337723a30882.bin', 'fileHash': 'fileHash=bce00351cfc559afec5beb90ea387b03788e4af5', 'fileType': 'fileType=PE32', 'malwareCategory': 'malwareCategory=Trojan_Generic', 'malwareSeverity': 'malwareSeverity=0.87', 'dst_country': 'dst_country=Bhutan'}  

# Post to Syslog

def post_syslog(msg, hostname):
    #print(msg)
    log = Syslog(host=hostname)
    log.send(msg,Level.INFO)


def syslog_message_format_raw(args,schemaSampledata,extenstion_data):
    try:
        if str(args.eventtype).lower() == 'cef':
            cef_header = {}
            cef_ext = {}
            template = 'CEF:{version}|{deviceVendor}|{deviceProduct}|{deviceVersion}|{signatureId}|{name}|{severity}|{extenstion_data}' 
            cef_header_fields = ['name', 'deviceVendor', 'deviceProduct', 'signatureId', 'version', 'deviceVersion', 'severity']
            cef_header_fields_dummy = {'version': '0', 'deviceVendor': 'CEF Vendor','deviceProduct': 'CEF Product','deviceVersion': 'CEF Version','signatureId': 'CEF Sig','name': 'CEF Attack Name','severity': 'CEF SEV'} 
            for field in cef_header_fields:
                if field in extenstion_data:
                    cef_header[field] = extenstion_data[field]
                else:
                    cef_header[field] = cef_header_fields_dummy[field]
            
            for field in extenstion_data:
                if not(field in cef_header_fields):
                    cef_ext[field] = "{}={}".format(field,extenstion_data[field])          
            #print(cef_header)
            prefixes = cef_header
            return_message = template.format(extenstion_data=' '.join(cef_ext.values()), **prefixes)
            #print (return_message)
        elif str(args.eventtype).lower() == 'syslog':
            #print("HEEEEEEEEEEEEEEEEEEEEREEEEEEEEEEEEEEEE")
            syslog_header = {}
            syslog_ext = {}
            #template = '<{priority}>{version} {ISOTimeStamp} {hostName} {application} {pid} {messageId} {structured_data} {message}'
            #template = schemaSampledata["SyslogMessage"]["syslog_message_template"]["values"]
            #template = "<{priority}>{version} {ISOTimeStamp} {hostName} {restofmessage}"
            template = "{hostName} {restofmessage}"
            syslog_header_fields = ['priority', 'version', 'ISOTimeStamp', 'hostName', 'restofmessage']
            #syslog_header_fields =  schemaSampledata["SyslogMessage"]["syslog_header_fields"]["values"]
            #syslog_header_fields_dummy = json.loads(schemaSampledata["SyslogMessage"]["syslog_header_fields_dummy"]["values"])
            #KVDelimiter = schemaSampledata["SyslogMessage"]["KVDelimiter"]["values"]
            #fieldDelimiter = schemaSampledata["SyslogMessage"]["fieldDelimiter"]["values"]
            #syslog_header_fields_dummy = {'priority': '139', 'version': '1','ISOTimeStamp': datetime.datetime.now(),'hostName': 'SYSLOG_Host','application': 'SYSLOG_App', 'pid': 'process','messageId': '1234'} 
            syslog_header_fields_dummy = {'priority': '139', 'version': '1','ISOTimeStamp': datetime.datetime.now(),'hostName': 'SYSLOG_Host','application': 'SYSLOG_App', 'pid': 'process','messageId': '1234'} 
            #print(syslog_header_fields_dummy)
            for field in syslog_header_fields:
                if field in extenstion_data:
                    syslog_header[field] = extenstion_data[field]
                else:
                    syslog_header[field] = syslog_header_fields_dummy[field]
            #print(syslog_header)
            for field in extenstion_data:
                if not(field in syslog_header_fields):
                    syslog_ext[field] = ("{}{}{}".format(field,KVDelimiter,extenstion_data[field]))        
            #print(syslog_ext)
            prefixes = syslog_header
            return_message = template.format(priority=syslog_header['priority'], version=syslog_header['version'],ISOTimeStamp=syslog_header['ISOTimeStamp'],hostName=syslog_header['hostName'],restofmessage=syslog_header['restofmessage'] )
            #print(return_message)
            #return_message = "Hellp"
        post_syslog(return_message, hostname=args.host) 
    except  Exception as e:
        print("syslog_message_format_raw  Exception {}",str(e))    

def get_dict_for_syslog_message(messge):
    header = messge.split(":",1)
    exten = {x: y for x, y in map(lambda x: x.split('='), shlex.split(messge))}


def build_message_from_raw(args,num):
    #print ("I am here")
    try:
        with open(args.input_file, 'r', encoding="utf8") as log_file:
            lines = log_file.readlines()
            if len(lines) >= 1:
                for record in lines:
                    #print(record)
                    if str(args.eventtype).lower() == 'syslog':
                        extenstion_data = pysyslog.parse(record)
                    if str(args.eventtype).lower() == 'cef':
                        extenstion_data = pycef.parse(record)
                    #print(extenstion_data)
                    headers = list(extenstion_data.keys())
                    #print(headers)
                    #cef_header = get_cef_header(headers,record.strip())
                    #print(cef_header)
                    if schemaSampledata != "NULL":
                        extenstion_data = build_custom_extension_for_raw(schemaSampledata,complete_header=headers, extensions=extenstion_data)
                        #cef_header = get_cef_header(headers,record.strip())
                        #print (extenstion_data)
                    syslog_message_format_raw(args,schemaSampledata,extenstion_data)
            else:
                extenstion_data = build_custom_extension_for_raw(schemaSampledata,complete_header=headers, extensions={})
                syslog_message_format_raw(args,schemaSampledata,extenstion_data)
            
            #print (extenstion_data)
    except OSError as e:
        print("Make sure input file exists with the header and try again. For now taking default sample event")
        extenstion_data = build_custom_extension_for_raw(schemaSampledata, complete_header=headers, extensions={})
        syslog_message_format_raw(args,schemaSampledata,extenstion_data)

#print("{extensions}".format(extensions=' '.join(extensions.values())))


# Building Syslog

def read_keys_sampledata(line):
    keys_bucket = []
    cefextdata = {}
    try:
        kvsearch = re.search("CEF:([0-9]\|[\w\s.\|]+)\|(.*)", line, re.IGNORECASE)
        if kvsearch:
            cef_header = kvsearch.group(1)
            kvpairs = kvsearch.group(2)
            print(cef_header)
            print(kvpairs)
            res =1
            while res:
                res = re.search("([0-9a-zA-Z]+)=(.*)", kvpairs, re.IGNORECASE)
                if res:
                    key = res.group(1)
                    kvpairs = res.group(2)
                    keys_bucket.append(key)
                    cefextdata[key] = kvpairs
        headers = set(keys_bucket)
        print(cefextdata)
        return headers
    except OSError as e:
        print("Make sure file exists with at least header, taking default header",e)
        return ['externalId', 'lastActivityTime', 'src', 'dst', 'src_hostname', 'dst_hostname', 'src_username', 'dst_username', 'dst_email_id', 'startTime', 'url', 'fileHash', 'fileType', 'malwareCategory', 'malwareSeverity', 'dst_country']
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
               protocol='UDP'):
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



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Syslog and CEF builder and replayer')
    parser.add_argument('input_file', metavar='DEFINITION_FILE', type=str, help='file containing sample events')
    parser.add_argument('--cust_file', metavar='EVENT_CUSTOMIZATIONS_FILE', type=str, default="None", help='Customizations defined here')
    parser.add_argument('--host', type=str, default='localhost', help='Syslog destination address')
    parser.add_argument('--port', type=int, default=514, help='Syslog destination port')
    parser.add_argument('--eventtype', type=str, default='CEF', help='CEF or Syslog')
    parser.add_argument('--eps', type=int, default=100, help='Max events')

    args = parser.parse_args()
    #print (args)
    
    """
    #args = []
    input_file = "C:\\Repositories\\Anki-Playground\\CEFReplicator\\syslog_meraki_raw.log"
    cust_file = "fortigate_customizations.json"
    host = "138.91.95.213"
    port = 514
    eventtype = "CEF"
    fileformat = "kvpair"
    eps = 100
    """
    #'C:\\Repositories\\Anki-Playground\\cefevent\\SampleData.csv'
    #print (args.input_file)
    schemaSampledata = "NULL"

    #print (headers)

    #if args.fileformat == "kvpair":
    #    headers = read_keys_sampledata(args.input_file)    

    with open(args.input_file, 'r', encoding="utf8") as log_file:
            lines = log_file.readlines()
            record_count = len(lines)


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
    except:
        KVDelimiter = "="
        print("Customization vaules not available takig default")  
    
    #print(schemaSampledata)

    if args.eventtype == 'syslog':
        KVDelimiter = KVDelimiter
    else:
        KVDelimiter = "="

    now = datetime.datetime.now()
    
    loop_break = 0
    total_records_sent = 0

    while not (loop_break):
        time_diff = (datetime.datetime.now() - now).total_seconds()
        if time_diff >= 9*60:
            loop_break = 1
            break    
        #eps = i / (time_diff if time_diff > 0 else 1)
        #if eps > args.eps:
        #    time.sleep(1)
        #    #now = datetime.datetime.now()
        else:
            total_records_sent = total_records_sent + record_count
            eps = total_records_sent / (time_diff if time_diff > 0 else 1)
            if eps > args.eps:
                time.sleep(1)
            #build_message_from_raw(args)
            p = worker(target=build_message_from_raw, args=(args,range(1,10)))
            p.start()
            p.join() 
        #print ("Sent {} messages till  with eps {} ".format(i,eps))

    #build_message_from_raw( args)


    
    #print (extenstion_data)
    #168.61.69.216