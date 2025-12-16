# Trend Micro TippingPoint

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Trend Micro |
| **Support Tier** | Partner |
| **Support Link** | [https://success.trendmicro.com/dcx/s/contactus?language=en_US](https://success.trendmicro.com/dcx/s/contactus?language=en_US) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20TippingPoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20TippingPoint) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Trend Micro TippingPoint via Legacy](../connectors/trendmicrotippingpoint.md)

**Publisher:** Trend Micro

The Trend Micro TippingPoint connector allows you to easily connect your TippingPoint SMS IPS events with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigation. This gives you more insight into your organization's networks/systems and improves your security operation capabilities.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias TrendMicroTippingPoint and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20TippingPoint/Parsers/TrendMicroTippingPoint).The function usually takes 10-15 minutes to activate after solution installation/update.

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
**2. Forward Trend Micro TippingPoint SMS logs to Syslog agent**

Set your TippingPoint SMS to send Syslog messages in ArcSight CEF Format v4.2 format to the proxy machine. Make sure you to send the logs to port 514 TCP on the machine's IP address.

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

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [TrendMicroTippingPoint.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20TippingPoint/Data%20Connectors/TrendMicroTippingPoint.json) |

[→ View full connector details](../connectors/trendmicrotippingpoint.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Trend Micro TippingPoint via Legacy](../connectors/trendmicrotippingpoint.md) |

[← Back to Solutions Index](../solutions-index.md)
