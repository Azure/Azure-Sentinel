# [Deprecated] Cisco Meraki

| | |
|----------|-------|
| **Connector ID** | `CiscoMeraki` |
| **Publisher** | Cisco |
| **Tables Ingested** | [`meraki_CL`](../tables-index.md#meraki_cl) |
| **Used in Solutions** | [CiscoMeraki](../solutions/ciscomeraki.md) |
| **Connector Definition Files** | [Connector_Syslog_CiscoMeraki.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki/Data%20Connectors/Connector_Syslog_CiscoMeraki.json) |

The [Cisco Meraki](https://meraki.cisco.com/) connector allows you to easily connect your Cisco Meraki (MX/MR/MS) logs with Microsoft Sentinel. This gives you more insight into your organization's network and improves your security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Custom Permissions:**
- **Cisco Meraki**: must be configured to export logs via Syslog

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias CiscoMeraki and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoMeraki/Parsers/CiscoMeraki.txt). The function usually takes 10-15 minutes to activate after solution installation/update.

**1. Install and onboard the agent for Linux**

Typically, you should install the agent on a different computer from the one on which the logs are generated.

>  Syslog logs are collected only from **Linux** agents.
**Choose where to install the agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**2. Configure the logs to be collected**

Follow the configuration steps below to get Cisco Meraki device logs into Microsoft Sentinel. Refer to the [Azure Monitor Documentation](https://docs.microsoft.com/azure/azure-monitor/agents/data-sources-json) for more details on these steps.
 For Cisco Meraki logs, we have issues while parsing the data by OMS agent data using default settings. 
So we advice to capture the logs into custom table **meraki_CL** using below instructions. 
1. Login to the server where you have installed OMS agent.
2. Download config file [meraki.conf](https://aka.ms/sentinel-ciscomerakioms-conf) 
		wget -v https://aka.ms/sentinel-ciscomerakioms-conf -O meraki.conf 
3. Copy meraki.conf to the /etc/opt/microsoft/omsagent/**workspace_id**/conf/omsagent.d/ folder. 
		cp meraki.conf /etc/opt/microsoft/omsagent/<<workspace_id>>/conf/omsagent.d/
4. Edit meraki.conf as follows:

	 a. meraki.conf uses the port **22033** by default. Ensure this port is not being used by any other source on your server

	 b. If you would like to change the default port for **meraki.conf** make sure that you dont use default Azure monitoring /log analytic agent ports I.e.(For example CEF uses TCP port **25226** or **25224**) 

	 c. replace **workspace_id** with real value of your Workspace ID (lines 14,15,16,19)
5. Save changes and restart the Azure Log Analytics agent for Linux service with the following command:
		sudo /opt/microsoft/omsagent/bin/service_control restart
6. Modify /etc/rsyslog.conf file - add below template preferably at the beginning / before directives section 
		$template meraki,"%timestamp% %hostname% %msg%\n" 
7. Create a custom conf file in /etc/rsyslog.d/ for example 10-meraki.conf and add following filter conditions.

	 With an added statement you will need to create a filter which will specify the logs coming from the Cisco Meraki to be forwarded to the custom table.

	 reference: [Filter Conditions — rsyslog 8.18.0.master documentation](https://rsyslog.readthedocs.io/en/latest/configuration/filters.html)

	 Here is an example of filtering that can be defined, this is not complete and will require additional testing for each installation.
		 if $rawmsg contains "flows" then @@127.0.0.1:22033;meraki
		 & stop
		 if $rawmsg contains "firewall" then @@127.0.0.1:22033;meraki
		 & stop
		 if $rawmsg contains "urls" then @@127.0.0.1:22033;meraki
		 & stop
		 if $rawmsg contains "ids-alerts" then @@127.0.0.1:22033;meraki
		 & stop
		 if $rawmsg contains "events" then @@127.0.0.1:22033;meraki
		 & stop
		 if $rawmsg contains "ip_flow_start" then @@127.0.0.1:22033;meraki
		 & stop
		 if $rawmsg contains "ip_flow_end" then @@127.0.0.1:22033;meraki
		 & stop 
8. Restart rsyslog
		 systemctl restart rsyslog
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Configure and connect the Cisco Meraki device(s)**

[Follow these instructions](https://documentation.meraki.com/General_Administration/Monitoring_and_Reporting/Meraki_Device_Reporting_-_Syslog%2C_SNMP_and_API) to configure the Cisco Meraki device(s) to forward syslog. Use the IP address or hostname for the Linux device with the Linux agent installed as the Destination IP address.

[← Back to Connectors Index](../connectors-index.md)
