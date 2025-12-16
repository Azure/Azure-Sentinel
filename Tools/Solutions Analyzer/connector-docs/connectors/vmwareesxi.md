# [Deprecated] VMware ESXi

| | |
|----------|-------|
| **Connector ID** | `VMwareESXi` |
| **Publisher** | VMWare |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [VMWareESXi](../solutions/vmwareesxi.md) |
| **Connector Definition Files** | [Connector_Syslog_VMwareESXi.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Data%20Connectors/Connector_Syslog_VMwareESXi.json) |

The [VMware ESXi](https://www.vmware.com/products/esxi-and-esx.html) connector allows you to easily connect your VMWare ESXi logs with Microsoft Sentinel This gives you more insight into your organization's ESXi servers and improves your security operation capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Custom Permissions:**
- **VMwareESXi**: must be configured to export logs via Syslog

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias VMwareESXi and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Parsers/VMwareESXi.yaml), on the second line of the query, enter the hostname(s) of your VMwareESXi device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.

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

Configure the facilities you want to collect and their severities.
 1. Under workspace advanced settings **Configuration**, select **Data** and then **Syslog**.
 2. Select **Apply below configuration to my machines** and select the facilities and severities.
 3.  Click **Save**.
- **Open Syslog settings**

**3. Configure and connect the VMware ESXi**

1. Follow these instructions to configure the VMWare ESXi to forward syslog: 
 - [VMware ESXi 3.5 and 4.x](https://kb.vmware.com/s/article/1016621) 
 - [VMware ESXi 5.0+](https://docs.vmware.com/en/VMware-vSphere/5.5/com.vmware.vsphere.monitoring.doc/GUID-9F67DB52-F469-451F-B6C8-DAE8D95976E7.html)
2. Use the IP address or hostname for the Linux device with the Linux agent installed as the Destination IP address.

[← Back to Connectors Index](../connectors-index.md)
