# Connect CyberArk to Azure Sentinel 

The CyberArk Syslog connector allows you to easily connect all your CyberArk security solution logs with your Azure Sentinel, to view dashboards, create custom alerts, and improve investigation. Integration between CyberArk and Azure Sentinel makes use of the CEF Data Connector to properly parse and display CyberArk Syslog messages.


> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Azure Sentinel.

## Configure and connect CyberArk EPV 

CyberArk Syslogs are sent from the Vault to a syslog staging server (rsyslog, syslog-ng), then the Linux Syslog agent exports the logs to Azure Sentinel.

1. In the Azure Sentinel portal, click Data connectors and select CyberArk and then Open connector page.

2. For more guidance on how to implement please refer to the Azure Sentinel tile in CyberArk MarketPlace.


## !!IMPORTANT NOTES!!
Due to the current way data is being presented the CEF strandard Custom Label functionality is not displaying properly. Here are the Custom Labels and their new column labels
|      Old Label     |       Sentinel Label      |    xsl KeyName   |
|:------------------:|:-------------------------:|:----------------:|
| Safe Name          | FileName                  | fname            |
| Device Type        | FileType                  | fileType         |
| Affected User Name | SourceUserPrivileges      | spriv            |
| Database           | DeviceExternalID          | deviceExternalId |
| Other info         | DestinationUserPrivileges | dpriv            |
| Request Id         | FileID                    | fileId           |
| Ticket Id          | OldFileID                 | oldFileId        |


## Find your data

After a successful connection is established, the data appears in Log Analytics under SecurityInsights CommonSecurityLog.
To use the relevant schema in Log Analytics for CyberArk, run the following query:
CommonSecurityLog \n| where DeviceVendor == \"Cyber-Ark\"\n| where DeviceProduct == \"Vault\".

## Validate connectivity
It may take upwards of 20 minutes until your logs start to appear in Log Analytics. 


## Next steps
In this document, you learned how to connect CyberArk to Azure Sentinel. To learn more about Azure Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](quickstart-get-visibility.md).
- Get started [detecting threats with Azure Sentinel](tutorial-detect-threats-built-in.md).
- [Use workbooks](tutorial-monitor-your-data.md) to monitor your data.

