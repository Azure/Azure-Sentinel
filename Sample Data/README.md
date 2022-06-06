This folder has sample data for different data connectors that can be leveraged by all Microsoft Sentinel contributions 

## Extracting ingested logs from Log Analytics Workspace
Ingested logs can be extracted by running a KQL query in the **Logs** window in Microsoft Sentinel/Log Analytics Workspace. Typing a basic query to get all all logs ingested by a Data Connector will get you the logs along with the defined schema. After you run the query, click on **Export** and then click **Export to CSV - all columns**

![ExportToCSV](Sample Data/Media/ExportToCSV.png)

## Extracting raw logs
We have several ways to capture the original data that comes from syslog devices and that is getting ingested into syslog-ng or rsyslog sever. One of the way is to capture the traces on syslog-ng or rsyslog server over 514 port. You can use the following command to captre the traffic into pacp file 
	
	sudo tcpdump -s 0 -Ani any port 514 -vv -w /var/log/syslog.pcap
	
![image](https://user-images.githubusercontent.com/10404181/171227166-a146f7e1-a27a-414e-9c68-bee23dee22a8.png)

Once we have the pcap file, we can visualize the events using utility "tcpick" and export into readable format
	
	tcpick -C -yP -r syslog.pcap > sampledata.log
	nano sampledata.log

![image](https://user-images.githubusercontent.com/10404181/171228705-d1ef47c8-25ad-4016-9a5f-14aaa2a61c51.png)