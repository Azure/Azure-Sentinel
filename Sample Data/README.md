This folder has sample data for different data connectors that can be leveraged by all Microsoft Sentinel contributions 

## Sample Data Contribution Guidance

Sample data is extremely useful when troubleshooting issues, supporting and/or enhancing the Data Connectors with more Security-focused content (such as Analytics, Hunting Queries, Workbooks, etc.). Wherever possible, sample data for each Data Connector should have two (2) files - the first should contain ingested logs exported after ingestion into a Log Analytics Workspace and the second should contain raw logs directly from the source of the logs. The following guidelines are designed to help committing sample data in a usable format into GitHub:
1.  The format for the file can be json (for API based Data Connector) / text (.txt) file (for Syslog/CEF based data Connectors) with the column names / property names adhering to the data type property names. Both ingested and raw logs hold relevance and are useful wherever these can be made available. Below are samples of the acceptable CEF and Syslog logs in their **raw** form:

    ```
     May 13 2022 12:05:52 10.0.0.0 dhcpd[30174]: DHCPDISCOVER from 0a:0b:0c:0d::0f via eth2 TransID 5daf9374: network 10.0.0.0/24: no free leases
     May 13 2022 12:05:52 10.1.1.1 named[11325]: zone voip.abc.com/IN: ZRQ applied transaction 0101010 with SOA serial 9191919. Zone version is now 0202020.
     May 13 2022 12:05:52 10.0.0.0 dhcpd[30174]: DHCPDISCOVER from 0a:0b:0c:0d::0f via eth2 TransID 5daf9374: network 10.0.0.0/24: no free leases
     May 13 2022 12:05:52 10.1.1.1 named[11325]: zone voip.abc.com/IN: ZRQ applied transaction 0101010 with SOA serial 9191919. Zone version is now 0202020.
     
     or

    1377449842.514782056 MX84 ids-alerts : signature=129:4:1 priority=3 timestamp=1377449842.512569 direction=ingress protocol=tcp/ip src=74.125.140.132:80
    1380664994.337961231 MX84 events : type=vpn_connectivity_change vpn_type='site-to-site' peer_contact='98.68.191.209:51856'   peer_ident='2814ee002c075181bb1b7478ee073860' connectivity='true'
    1377448470.246576346 MX84 ids-alerts : signature=119:15:1 priority=2 timestamp=1377448470.238064 direction=egress protocol=tcp/ip src=192.168.111.254:56240     signature=1:28423:1 priority=1 timestamp=1468531589.810079 dhost=98:5A:EB:E1:81:2F direction=ingress protocol=tcp/ip src=151.101.52.238:80 dst=192.168.128.2:53023  message: EXPLOIT-KIT Multiple exploit kit single digit exe detection url=http://www.eicar.org/download/eicar.com.txt src=192.168.128.2:53150 dst=188.40.238.250:80  mac=98:5A:EB:E1:81:2F name='EICAR:EICAR_Test_file_not_a_virus-tpd'// 1563249630.774247467 remote_DC1_appliance security_event ids_alerted signature=1:41944:2 priority=1 timestamp=TIMESTAMPEPOCH.647461 dhost=74:86:7A:D9:D7:AA direction=ingress 
    ```
>**Note**: Ingested logs are logs exported after ingesting into a Log Analytics Workspace.

Data Connectors that depend on APIs for log collection make raw logs available in the json format which can be uploaded.

2. Submit the sample data via a GitHub PR to the ['Sample data' folder](https://aka.ms/azuresentinelgithubsampledata) in the right subfolder - CEF / Syslog / Custom depending on the type of data connector. Create a new folder under the Sample data folder. The folder name must be same as the name of the Data Connector. Under the folder created, the following two files must be created:
    1. **IngestedLogs.json** - This file should contain an export of the logs after they've been ingested into the Log Analytics workspace. 
    2. **RawLogs** - This file must have the raw logs in the format described above. This file can have a **.txt** extension if the Data Connector is Syslog/CEF based or **.json** if the Data Connector is API based.
>Guidance on how to extract ingested and raw logs can be found below.
3. Important: Please ensure all sample data has been scrubbed to remove all sensitive PII information that may exist in the logs. The intent is to understand the "what" and "how" from the logs not the "who".

## Extracting ingested logs from Log Analytics Workspace
Ingested logs can be extracted by running a KQL query in the **Logs** window in Microsoft Sentinel/Log Analytics Workspace. Typing a basic query to get all all logs ingested by a Data Connector will get you the logs along with the defined schema. After you run the query, click on **Export** and then click **Export to CSV - all columns**

![ExportToCSV](https://github.com/Azure/Azure-Sentinel/blob/prtanej-SampleDataGuidanceUpdate/Sample%20Data/Media/ExportToCSV.png)

## Extracting raw logs
We have several ways to capture the original data that comes from syslog devices and that is getting ingested into syslog-ng or rsyslog sever. One of the way is to capture the traces on syslog-ng or rsyslog server over 514 port. You can use the following command to captre the traffic into pacp file 
	
	sudo tcpdump -s 0 -Ani any port 514 -vv -w /var/log/syslog.pcap
	
![image](https://user-images.githubusercontent.com/10404181/171227166-a146f7e1-a27a-414e-9c68-bee23dee22a8.png)

Once we have the pcap file, we can visualize the events using utility "tcpick" and export into readable format
	
	tcpick -C -yP -r syslog.pcap > sampledata.log
	nano sampledata.log

![image](https://user-images.githubusercontent.com/10404181/171228705-d1ef47c8-25ad-4016-9a5f-14aaa2a61c51.png)
