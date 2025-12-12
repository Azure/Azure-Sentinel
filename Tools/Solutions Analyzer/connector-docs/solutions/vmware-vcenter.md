# VMware vCenter

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20vCenter](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20vCenter) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] VMware vCenter](../connectors/vmwarevcenter.md)

**Publisher:** VMware

The [vCenter](https://www.vmware.com/in/products/vcenter-server.html) connector allows you to easily connect your vCenter server logs with Microsoft Sentinel. This gives you more insight into your organization's data centers and improves your security operation capabilities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Include custom pre-requisites if the connectivity requires - else delete customs**: Description for any custom pre-requisite

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias VMware vCenter and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20vCenter/Parsers/vCenter.txt), on the second line of the query, enter the hostname(s) of your VMware vCenter device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update. 
> 1. If you have not installed the vCenter solution from ContentHub then [Follow the steps](https://aka.ms/sentinel-vCenter-parser) to use the Kusto function alias, **vCenter**

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

Follow the configuration steps below to get vCenter server logs into Microsoft Sentinel. Refer to the [Azure Monitor Documentation](https://docs.microsoft.com/azure/azure-monitor/agents/data-sources-json) for more details on these steps.
 For vCenter Server logs, we have issues while parsing the data by OMS agent data using default settings. 
So we advice to capture the logs into custom table **vcenter_CL** using below instructions. 
1. Login to the server where you have installed OMS agent.
2. Download config file vCenter.conf 
		wget -v https://aka.ms/sentinel-vcenteroms-conf -O vcenter.conf 
3. Copy vcenter.conf to the /etc/opt/microsoft/omsagent/**workspace_id**/conf/omsagent.d/ folder. 
		cp vcenter.conf /etc/opt/microsoft/omsagent/<<workspace_id>>/conf/omsagent.d/
4. Edit vcenter.conf as follows:

	 a. vcenter.conf uses the port **22033** by default. Ensure this port is not being used by any other source on your server

	 b. If you would like to change the default port for **vcenter.conf** make sure that you dont use default Azure monotoring /log analytic agent ports I.e.(For example CEF uses TCP port **25226** or **25224**) 

	 c. replace **workspace_id** with real value of your Workspace ID (lines 13,14,15,18)
5. Save changes and restart the Azure Log Analytics agent for Linux service with the following command:
		sudo /opt/microsoft/omsagent/bin/service_control restart
6. Modify /etc/rsyslog.conf file - add below template preferably at the beginning / before directives section 

		$template vcenter,"%timestamp% %hostname% %msg%\ n" 

 **Note - There is no space between slash(\\) and character 'n' in above command.**

 7. Create a custom conf file in /etc/rsyslog.d/ for example 10-vcenter.conf and add following filter conditions.

Download config file [10-vCenter.conf](https://aka.ms/sentinel-vcenter-conf)

	 With an added statement you will need to create a filter which will specify the logs coming from the vcenter server to be forwarded to the custom table.

	 reference: [Filter Conditions — rsyslog 8.18.0.master documentation](https://rsyslog.readthedocs.io/en/latest/configuration/filters.html)

	 Here is an example of filtering that can be defined, this is not complete and will require additional testing for each installation.
		 if $rawmsg contains "vcenter-server" then @@127.0.0.1:22033;vcenter
		 & stop 
		 if $rawmsg contains "vpxd" then @@127.0.0.1:22033;vcenter
		 & stop
		 
8. Restart rsyslog
		 systemctl restart rsyslog
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Configure and connect the vCenter device(s)**

[Follow these instructions](https://docs.vmware.com/en/VMware-vSphere/7.0/com.vmware.vsphere.monitoring.doc/GUID-9633A961-A5C3-4658-B099-B81E0512DC21.html) to configure the vCenter to forward syslog. Use the IP address or hostname for the Linux device with the Linux agent installed as the Destination IP address.

| | |
|--------------------------|---|
| **Tables Ingested** | `vcenter_CL` |
| **Connector Definition Files** | [Connector_Syslog_vcenter.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMware%20vCenter/Data%20Connectors/Connector_Syslog_vcenter.json) |

[→ View full connector details](../connectors/vmwarevcenter.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `vcenter_CL` | [[Deprecated] VMware vCenter](../connectors/vmwarevcenter.md) |

[← Back to Solutions Index](../solutions-index.md)
