# Syslog or CEF over Syslog data replication
Author: Anki Narravula - Reachout to anknar@microsoft.com incase of any issues or clarifications required

## Description
This repository contains a console application (Python) that helps to replicate data in Syslog or CEF over syslog format by using sample events. Users need to input a file with sample data in it (minimum 1 event) to start generating the syslog traffic. User can use this tool to mimic as any Syslog datasource (device). Data will be sent to a specified destination address (where we have AMA / LA agent installed here to receive the data) over TCP or UDP 514 port. Further AMA/LA agent can send to Sentinel as per configurations defined on the agent node. To deploy a log forwarder to ingest Syslog and CEF logs to Microsoft Sentinel refer - https://docs.microsoft.com/azure/sentinel/connect-log-forwarder?tabs=rsyslog

   If you are trying to see specific values for the fields (in case of CEF data), for example deviceVendor need to be always from the array of values ["Fortinet","CISCO","Microsoft"] or any timestamp field should set to current etc then we need to input a file where we have such customizations defined. Otherwise we dont require to input this file.

## Prerequisites

- Make sure we have python installed on the system where we are running this utility
- Sample data (File name and path) is mandatory parameter for invocation. Make sure you have it ready
- Log forwarding agent is configured already and have IP Address and host name handy
- Make sure firewall is not blockiign the traffic flow from source (where we are running this utlity) and destination (where we have log forwarder configured)

## How to use 

We have 2 flavors
1.	Generating syslog / cef traffic using raw log
2.	Generating syslog / cef traffic using csv file (deprecated)
	
### 1. Generating syslog / cef traffic using raw log

- Step 0: Download the package 
	```
		sudo apt-get install zip unzip
		wget https://github.com/Azure/Azure-Sentinel/blob/SyslogDataReplication/Tools/Syslog-cef-data-replicator/syslog_cef_data_replicator.zip?raw=true
		unzip syslog_cef_data_replicator.zip
	```

- Step 1: Make sure raw log present in a file (with any extension) and each record separated by new line char (\n)

     For example:

     Inflobox NIOS raw logs:
       
       
       May 13 2022 12:05:52 10.0.0.0 dhcpd[30174]: DHCPDISCOVER from 0a:0b:0c:0d::0f via eth2 TransID 5daf9374: network 10.0.0.0/24: no free leases
       May 13 2022 12:05:52 10.1.1.1 named[11325]: zone voip.abc.com/IN: ZRQ applied transaction 0101010 with SOA serial 9191919. Zone version is now 0202020.
       May 13 2022 12:05:52 10.0.0.0 dhcpd[30174]: DHCPDISCOVER from 0a:0b:0c:0d::0f via eth2 TransID 5daf9374: network 10.0.0.0/24: no free leases
       May 13 2022 12:05:52 10.1.1.1 named[11325]: zone voip.abc.com/IN: ZRQ applied transaction 0101010 with SOA serial 9191919. Zone version is now 0202020.
       

     CISCO Meraki raw logs:
       
       1377449842.514782056 MX84 ids-alerts : signature=129:4:1 priority=3 timestamp=1377449842.512569 direction=ingress protocol=tcp/ip src=74.125.140.132:80
       1380664994.337961231 MX84 events : type=vpn_connectivity_change vpn_type='site-to-site' peer_contact='98.68.191.209:51856'   peer_ident='2814ee002c075181bb1b7478ee073860' connectivity='true'
       1377448470.246576346 MX84 ids-alerts : signature=119:15:1 priority=2 timestamp=1377448470.238064 direction=egress protocol=tcp/ip src=192.168.111.254:56240     signature=1:28423:1 priority=1 timestamp=1468531589.810079 dhost=98:5A:EB:E1:81:2F direction=ingress protocol=tcp/ip src=151.101.52.238:80 dst=192.168.128.2:53023  message: EXPLOIT-KIT Multiple exploit kit single digit exe detection url=http://www.eicar.org/download/eicar.com.txt src=192.168.128.2:53150 dst=188.40.238.250:80  mac=98:5A:EB:E1:81:2F name='EICAR:EICAR_Test_file_not_a_virus-tpd'// 1563249630.774247467 remote_DC1_appliance security_event ids_alerted signature=1:41944:2 priority=1 timestamp=TIMESTAMPEPOCH.647461 dhost=74:86:7A:D9:D7:AA direction=ingress protocol=tcp/ip src=23.6.199.123:80 dst=10.1.10.51:56938 message: BROWSER-IE Microsoft Edge scripting engine security bypass css attempt
       1380653443.857790533 MR18 events : type=device_packet_flood radio='0' state='end' alarm_id='4' reason='left_channel' airmarshal_events type= rogue_ssid_detected ssid='' bssid='02:18:5A:AE:56:00' src='02:18:5A:AE:56:00' dst='02:18:6A:13:09:D0' wired_mac='00:18:0A:AE:56:00' vlan_id='0' channel='157' rssi='21' fc_type='0' fc_subtype='5'
       1380653443.857790533 MS220_8P events : type=8021x_eap_success port='' identity='employee@ikarem.com'
       1374543213.342705328 MX84 urls : src=192.168.1.186:63735 dst=69.58.188.40:80 mac=58:1F:AA:CE:61:F2 request: GET https://...
       1374543986.038687615 MX84 flows : src=192.168.1.186 dst=8.8.8.8 mac=58:1F:AA:CE:61:F2 protocol=udp sport=55719 dport=53 pattern: allow all
       

- Step 2: Save in same folder as script exist, name and extension can be any thing. If file is at different location then we need to provide complete path
- Step 3: Navigate to the script path, where syslogfromraw.py exists
          For example, if script exists in C:\Repositories\Anki-Playground\SyslogReplicator then run
		cd C:\Repositories\Anki-Playground\SyslogReplicator
- Step 4: You can try with the following commands
 	
	```
	1.	python syslogfromraw.py --host "13.87.202.58" --port 514 --eventtype "syslog" --cust_file fortigate_customizations.json syslog_meraki_raw.log     
	2.	python syslogfromraw.py --host "13.87.202.58" --port 514 --eventtype "syslog" syslog_meraki_raw.log
	3.	python syslogfromraw.py --host "13.87.202.58" --port 514 --eventtype "cef" --cust_file fortigate_customizations.json cef_microsoft_ata.log   
	4.	python syslogfromraw.py --host "13.87.202.58" --port 514 --eventtype "cef"  cef_microsoft_ata.log        
	

     arguments:

	--cust_file (optional – Name of the file where we have customizations defined)
	--port (optional – default is 514 if not specified)
	--host  (optional – default is localhost if not specified)
	--eventtype  (optional – default is cef if not specified)
	--eps  (optional – default is 100 if not specified)
	Name of the file where we have same data is mandatory like python syslogfromcsv.py cef_microsoft_ata.log
	```
- Step 5: (Optional) Run the script multiple time to achieve higer EPS.

 	During testing we have observed that with single invocation of this script we can get upto 100 EPS volume. If you want to get the more EPS, you need to run the 	script multiple times in the in the background.
	```
	#!/usr/bin/env python3
	chmod +x syslogfromraw.py
	nohup /path/to/syslogfromraw.py &
	or
	nohup python /path/to/syslogfromraw.py &
	```
- Step 6: (Optional) Use azure batch account and data factory for achieving higher EPS

	Setting up batch account and VMs pool
	- You can find the details here https://docs.microsoft.com/azure/batch/accounts and https://docs.microsoft.com/azure/batch/nodes-and-pools
	
	Upload scripts and sample data (and customization file) to storage account
	- Find more details here - https://docs.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-portal
	 
	Create data factory pipeline with azure batch task 
	- You can find more details here - https://techcommunity.microsoft.com/t5/azure-paas-blog/configure-a-simple-azure-batch-job-with-azure-data-factory/ba-p/2260759
	
	Schedule data factory job to run for every 10 minutes
	- More details are here  - https://docs.microsoft.com/azure/data-factory/how-to-create-schedule-trigger?tabs=data-factory
	
	Important tips:
	
	- Have 1 task(activity) for each 100 EPS (during our testing, we found out that this is ideal)
		- For example, If you want 5000 EPS throuput, then have 50 parallell tasks / activities running (each task throughputs 100 EPS)
		- ![image](https://user-images.githubusercontent.com/10404181/186093885-3c7bfd1c-2e58-4328-b296-bf017d23b564.png)
	
	- Schedule pipeline with 10 mins frequency and enable to kill previous taks before starting new activity. (Set timeout to lesser than 10 minutes)
		- ![image](https://user-images.githubusercontent.com/10404181/186095028-d4854978-d4fd-4866-8756-223fd59d69c8.png)
	
	- Use local ip addres to send the logs (which will give good throuput). Have agent and batch account's nodes in the same network
		- ![image](https://user-images.githubusercontent.com/10404181/186095413-6bb22cb0-2e64-4b3a-a2c8-0e1c6dadeb20.png)
	
	```
	python syslogfromraw.py --host "10.4.87.1" --port 514 --eventtype "syslog" --cust_file fortigate_customizations.json syslog_meraki_raw.log
	python syslogfromraw.py --host "localhost" --port 514 --eventtype "syslog" --cust_file fortigate_customizations.json syslog_meraki_raw.log 
	```
	
	- If possible have agent installed locally on the batch account nodes
	- On Agent node - Make sure you stop the logging into /var/log/syslog, otherwise you may get into memory issues
	
	```
	cd /etc/rsyslog.d/
	nano 50-default.conf
	//Comment the line that stores the logs into /var/log/syslog
	service rsyslog restart
	```
	
### 2. Generating syslog / cef traffic using csv file

- Step 1: Make sure csv file present with header and at least 1 record, records are separated by new line char (\n)
        For example:
         FortiGate sample data in syslog converted into csv:
 
	![image](https://user-images.githubusercontent.com/10404181/170849664-3442063e-a401-4166-87b0-7ac90429c4d3.png)

    Note: For CEF traffic, make sure header fields also exists in csv along with the structured data.
 
- Step 2: Save in same folder as script exist, name and extension can be any thing
- Step 3: Navigate to the script path, where syslogfromraw.py exists
		For example, if script exists in C:\Repositories\Anki-Playground\SyslogReplicator then run
		cd C:\Repositories\Anki-Playground\SyslogReplicator
- Step 4: You can try with the following commands

	```
	1. python syslogfromcsv.py --host "13.87.202.58" --port 514 --eventtype "syslog" --cust_file 'fortigate_customizations.json' syslog_fortigate_sample_data.csv 
	2. python syslogfromcsv.py --host "13.87.202.58" --port 514 --eventtype "syslog" syslog_fortigate_sample_data.csv 
	3. python syslogfromcsv.py --host "13.87.202.58" --port 514 --eventtype ‘cef’ --cust_file 'fortigate_customizations.json' cef_fortigate_sample_data.csv 
	4. python syslogfromcsv.py --host "13.87.202.58" --port 514 --eventtype ‘cef’  cef_fortigate_sample_data.csv

	arguments:
	--cust_file (optional – Name of the file where we have customizations defined)
	--port (optional – default is 514 if not specified)
	--host  (optional – default is localhost if not specified)
	--eventtype  (optional – default is cef if not specified)
	--eps  (optional – default is 100 if not specified)
	Name of the file where we have same data is mandatory like python syslogfromcsv.py cef_fortigate_sample_data.csv
	```

## Additional information:

### How to capture the original or raw data
We have several ways to capture the original data that comes from syslog devices and that is getting ingested into syslog-ng or rsyslog sever. One of the way is to capture the traces on syslog-ng or rsyslog server over 514 port. You can use the following command to captre the traffic into pacp file 
	
	sudo tcpdump -s 0 -Ani any port 514 -vv -w /var/log/syslog.pcap
	
![image](https://user-images.githubusercontent.com/10404181/171227166-a146f7e1-a27a-414e-9c68-bee23dee22a8.png)

Once we have the pcap file, we can visualize the events using utility "tcpick" and export into readable format
	
	tcpick -C -yP -r syslog.pcap > sampledata.log
	nano sampledata.log

![image](https://user-images.githubusercontent.com/10404181/171228705-d1ef47c8-25ad-4016-9a5f-14aaa2a61c51.png)


You use the file sampledata.log further as input for this utility to replicate the data.

### Log customizations:
While replaying the events, if you would like to customize any fields values (for example src must be one of the IPs from an array _[“23.2.3.42”,”78.3.78.2”,”34.98.0.9”]_ ) this comes handy. You just can mention the name of the field and desired values. Our script picks up the customizations and original values will be replaced with the custom values. 

For example, see below how the customization defiled – 

		
	"customizations":{
        "version":{"data_type":"Integer", "values": [0]},
        "deviceVendor": {"data_type":"String", "values": ["CISCO","JUNIPER","Fortinet","MSFT"]},
        "deviceProduct": {"data_type":"String", "values": ["Cortex","Vertex","Fortigate", "WSF"]},
        "deviceVersion": {"data_type":"String", "values": ["2","19","34"]},
        "signatureId": {"data_type":"String", "values": ["3.6.0.3","3.4.0.6","5.6.7.8","1.6.1.3","9.6.1.7","1.9.0.2","1.89.12.3","14.61.0.31","19.6.01.36"]},
        "name": {"data_type":"String", "values": ["Phishing","TROJAN_GIPPERS.DC","services-health","Monitoring"]},
        "severity": {"data_type":"Integer", "values": [1,2,3,4,5,6,7,8,9]},
        "deviceExternalId": {"data_type":"String", "values": ["FGVMEV9XTHSMYCCF","FGVMEV9XPDFRYYCCF","FGVMEV9XPEPFOCFR"]},
        "FTNTFGTlogid": {"data_type":"String", "values": ["0100026001","010004554","01566fjj56"]},
        "cat": {"data_type":"String", "values": ["event","alert","traffic"]},
        "direction": {"data_type":"String", "values": ["egress","ingress","in"]},
        "FTNTFGTsubtype": {"data_type":"String", "values": ["system"]},
        "origisationname": {"data_type":"String", "values": ["Fortigate","CISCO"]},
        "origin": {"data_type":"String", "values": ["NA","NULL",""]},
        "logid": {"data_type":"String", "values": ["562ed3w","dfdf564s","3455frs"]},
        "dst_country": {"data_type":"String", "values": ["US","Canada","Bhutan"]},
        "dst": {"data_type":"String", "values": ["67.21.32.78","201.32.13.56","76.62.201.10"]},
        "src": {"data_type":"String", "values": ["101.21.21.1","67.23.21.90","82.78.9.87"]},
        "ifname": {"data_type":"String", "values": ["eth0","eth1"]},
        "product": {"data_type":"String", "values": ["FortiWeb","Prisma","Fortigate", "WAF"]},
        "dpt": {"data_type":"Integer", "values": [1233, 3456, 6738]},
        "spt": {"data_type":"Integer", "values": [7837,8929,7832,8729]},
        "start": {"data_type":"datetime", "values": ["current"], "format":"%Y-%m-%d %H:%M:%S"},
        "end": {"data_type":"datetime", "values": ["current"], "format":"%Y-%m-%d %H:%M:%S"},
        "ISOTimeStamp": {"data_type":"datetime", "values": ["current"], "format":"%Y-%m-%d %H:%M:%S"}    
	} 
	

  Store above customizations into a json file as pass file name as an argument (--cust_file) as shown below
 
When we have customizations defined, field values from sample events will be replaced by the custom values that are defined in this section. 

### Visualizing events: 

	Coming soon

### Troubleshooting:

   If you are not running this utility where we have LA agent installed and facing some issues, follow guidelines  – 
	
	https://dev.azure.com/SupportabilityWork/Azure Security/_wiki/wikis/Azure Sentinel CSS wiki/3822/CEF-Syslog-Step-by-Step-Troubleshooter
	https://dev.azure.com/SupportabilityWork/Azure Security/_wiki/wikis/Azure Sentinel CSS wiki/1345/Syslog-Workflow-ASA-Check-Point-Syslog-Palo-Alto-Fortigate-Cisco-CEF
	
   If you are running locally (where we have LA forwarder installed) then you may not require to validate remote communication part of it, check other troubleshooting steps  
