# SonicWall Firewall connector for Microsoft Sentinel

Common Event Format (CEF) is an industry standard format on top of Syslog messages, used by SonicWall to allow event interoperability among different platforms.
By connecting your CEF logs to Microsoft Sentinel, you can take advantage of search & correlation, alerting, and threat intelligence enrichment for each log.

## Query samples
**All logs**
```Kusto
CommonSecurityLog
| where DeviceVendor == "SonicWall"
| sort by TimeGenerated
```

**Summarize by destination IP and port**
```Kusto
CommonSecurityLog
| where DeviceVendor == "SonicWall"
| summarize count() by DestinationIP, DestinationPort, TimeGenerated
| sort by TimeGenerated
```

**Show all dropped traffic from the SonicWall Firewall**
```Kusto
CommonSecurityLog
| where DeviceVendor == "SonicWall"
| where AdditionalExtensions has 'fw_action="drop"' or Message has "blocked" or Message has "dropped" or Activity has "dropped" or Activity has "blocked" or Message has "prevention" or Message has "Gateway Anti-Virus Alert:"
```


## Installation instructions
### 1. Linux Syslog agent configuration
Install and configure the Linux agent to collect your Common Event Format (CEF) Syslog messages and forward them to Microsoft Sentinel.

> Notice that the data from all regions will be stored in the selected workspace


#### 1.1 Select or create a Linux machine
Select or create a Linux machine that Microsoft Sentinel will use as the proxy between your security solution and Microsoft Sentinel this machine can be on your on-prem environment, Azure or other clouds.


#### 1.2 Install the CEF collector on the Linux machine
Install the Microsoft Monitoring Agent on your Linux machine and configure the machine to listen on the necessary port and forward messages to your Microsoft Sentinel workspace. The CEF collector collects CEF messages on port 514 TCP.

> 1. Make sure that you have Python on your machine using the following command: python -version.
> 2. You must have elevated permissions (sudo) on your machine.

Run the following command to install and apply the CEF collector:

`sudo wget -O cef_installer.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_installer.py&&sudo python cef_installer.py {0} {1}`


#### 2. Forward SonicWall Firewall Common Event Format (CEF) logs to Syslog agent
Set your SonicWall firewall to send Syslog messages in CEF format to the proxy machine.
Make sure you send the logs to UDP/514 on the machine's IP address.


[How can I configure a syslog server on a SonicWall firewall?
](https://www.sonicwall.com/support/knowledge-base/how-can-i-configure-a-syslog-server-on-a-sonicwall-firewall/170505984096810/)

> - Select *local use 4* as the facility.
> - Select *ArcSight* as the Syslog format.
> - It is recommended to secure the Syslog communication between the firewall and the CEF collector, particularly if that connector is on the WAN.


#### 3. Validate connection
Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

> It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

> 1. Make sure that you have Python on your machine using the following command: python -version
> 2. You must have elevated permissions (sudo) on your machine

Run the following command to validate your connectivity:

`sudo wget -O cef_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_troubleshoot.py&&sudo python cef_troubleshoot.py {0}`


#### 4. Secure your machine
Make sure to configure the machine's security according to your organization's security policy

[Learn more](https://learn.microsoft.com/en-us/azure/sentinel/connect-common-event-format#security-considerations)

[SonicWall Network Security for Microsoft Sentinel in the Azure Marketplace](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/sonicwall-inc.sonicwall-networksecurity-azure-sentinal?tab=Overview)