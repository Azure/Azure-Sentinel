# IronNet IronDefense

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [IronNet IronDefense](../connectors/ironnetirondefense.md)

**Publisher:** IronNet

The IronNet IronDefense connector enables ingest of IronDefense alerts, events, and IronDome notifications into Sentinel, enabling Sentinel to utilize IronDefense's behavioral analytics and the IronDome community to quickly identify threats in your enterprise network.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Linux Syslog agent configuration**

Install and configure the Linux agent to collect your Common Event Format (CEF) Syslog messages and forward them to Microsoft Sentinel.

> Notice that the data from all regions will be stored in the selected workspace
**1.1 Select or create a Linux machine**

  Select or create a Linux machine that Microsoft Sentinel will use as the proxy between your security solution and Microsoft Sentinel this machine can be on your on-prem environment, Azure or other clouds.

  **1.2 Install the CEF collector on the Linux machine**

  Install the Microsoft Monitoring Agent on your Linux machine and configure the machine to listen on the necessary port and forward messages to your Microsoft Sentinel workspace. The CEF collector collects CEF messages on port 514 TCP.

> 1. Make sure that you have Python on your machine using the following command: python -version.

> 2. You must have elevated permissions (sudo) on your machine.
  - **Run the following command to install and apply the CEF collector:**: `sudo wget -O cef_installer.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_installer.py&&sudo python cef_installer.py {0} {1}`
**2. Forward Common Event Format (CEF) logs to Syslog agent**

Configure the IronNet Data Collector to send alerts, events, and IronDome notifications in CEF format to the proxy machine. Make sure you to send the logs to port 514 TCP on the machine's IP address.
**2.1 Deploy the IronNet Data Collector VM**

  Deploy the IronNet Data Collector VM using the image provided by your IronNet representative.

  **2.2 Configure the IronAPI connector using the Data Collector wizard.**

  Ssh into the Data Collector VM as the config user and use the Data Collector configuration wizard to configure the IronAPI connector to receive notifications from IronDefense and forward them to your Microsoft Sentinel workspace. You will need:

> 1. IronAPI credentials.

> 2. IronDefense hostname.

> 3. The public IP of the linux machine running the CEF collector.
  - **Run the following command to launch the Data Collector configuration wizard:**: `wizard`

  **2.2 Verify IronAPI connector configuration**

  Verify the IronAPI connector has been configured properly and is running normally.
  - **Run the following command to view the logs in the IronAPI connector. If no errors occur after 5 minutes, the connector is running normally.**: `sudo journalctl -f CONTAINER_NAME=ironapi-notifications-collector`
**3. Validate connection**

Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

>It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

> 1. Make sure that you have Python on your machine using the following command: python -version

>2. You must have elevated permissions (sudo) on your machine
- **Run the following command to validate your connectivity:**: `sudo wget  -O cef_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_troubleshoot.py&&sudo python cef_troubleshoot.py  {0}`

**4. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [IronNetIronDefense.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/IronNet%20IronDefense/Data%20Connectors/IronNetIronDefense.json) |

[→ View full connector details](../connectors/ironnetirondefense.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [IronNet IronDefense](../connectors/ironnetirondefense.md) |

[← Back to Solutions Index](../solutions-index.md)
