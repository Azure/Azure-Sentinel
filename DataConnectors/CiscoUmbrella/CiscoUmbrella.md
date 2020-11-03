# Connect your Cisco Umbrella to Azure Sentinel 



Cisco Umbrella connector allows you to easily connect all your Cisco Umbrella security solution logs with your Azure Sentinel, to view dashboards, create custom alerts, and improve investigation. Integration between Cisco Umbrella and Azure Sentinel makes use of REST API.


> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Azure Sentinel.

## Configure and connect Cisco Umbrella 

Cisco Umbrella can integrate and export logs directly to Azure Sentinel.
1. In the Azure Sentinel portal, click Data connectors and select Cisco Umbrella and then Open connector page.

2. Follow the steps described in the "Configuration" section of the connector page.


## Find your data

After a successful connection is established, the data appears in Log Analytics under CustomLogs Cisco_Umbrella_dns_CL, Cisco_Umbrella_proxy_CL, Cisco_Umbrella_ip_CL, Cisco_Umbrella_cloudfirewall_CL.

## Validate connectivity
It may take upwards of 20 minutes until your logs start to appear in Log Analytics. 
