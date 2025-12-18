# SecurityBridge App

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | SecurityBridge |
| **Support Tier** | Partner |
| **Support Link** | [https://securitybridge.com/contact/](https://securitybridge.com/contact/) |
| **Categories** | domains,verticals |
| **First Published** | 2022-02-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge%20App](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge%20App) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [SecurityBridge Solution for SAP](../connectors/securitybridge.md)

**Publisher:** SecurityBridge Group GmbH

### [SecurityBridge Threat Detection for SAP](../connectors/securitybridgesap.md)

**Publisher:** SecurityBridge

SecurityBridge is the first and only holistic, natively integrated security platform, addressing all aspects needed to protect organizations running SAP from internal and external threats against their core business applications. The SecurityBridge platform is an SAP-certified add-on, used by organizations around the globe, and addresses the clients’ need for advanced cybersecurity, real-time monitoring, compliance, code security, and patching to protect against internal and external threats.This Microsoft Sentinel Solution allows you to integrate SecurityBridge Threat Detection events from all your on-premise and cloud based SAP instances into your security monitoring.Use this Microsoft Sentinel Solution to receive normalized and speaking security events, pre-built dashboards and out-of-the-box templates for your SAP security monitoring.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

*NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias SecurityBridgeLogs and load the function code or click [here](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge%20App/Parsers/SecurityBridgeLogs.txt).The function usually takes 10-15 minutes to activate after solution installation/update.

>**NOTE:** This data connector has been developed using SecurityBridge Application Platform 7.4.0.

**1. Install and onboard the agent for Linux or Windows**

This solution requires logs collection via an Microsoft Sentinel agent installation

>  The Microsoft Sentinel agent is supported on the following Operating Systems:  
1. Windows Servers 
2. SUSE Linux Enterprise Server
3. Redhat Linux Enterprise Server
4. Oracle Linux Enterprise Server
5. If you have the SAP solution installed on HPUX / AIX then you will need to deploy a log collector on one of the Linux options listed above and forward your logs to that collector
**Choose where to install the Linux agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**Choose where to install the Windows agent:**

**Install agent on Azure Windows Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install/configure: InstallAgentOnVirtualMachine**

  **Install agent on a non-Azure Windows Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install/configure: InstallAgentOnNonAzure**

**2. Configure the logs to be collected**

Configure the custom log directory to be collected
- **Open custom logs settings**

1. Select the link above to open your workspace advanced settings 
2. Click **+Add custom**
3. Click **Browse** to upload a sample of a SecurityBridge SAP log file (e.g. AED_20211129164544.cef). Then, click **Next >**
4. Select **New Line** as the record delimiter then click **Next >**
5. Select **Windows** or **Linux** and enter the path to SecurityBridge logs based on your configuration. Example:
 - '/usr/sap/tmp/sb_events/*.cef' 

>**NOTE:** You can add as many paths as you want in the configuration.

6. After entering the path, click the '+' symbol to apply, then click **Next >** 
7. Add **SecurityBridgeLogs** as the custom log Name and click **Done**

**3. Check logs in Microsoft Sentinel**

Open Log Analytics to check if the logs are received using the SecurityBridgeLogs_CL Custom log table.

>**NOTE:** It may take up to 30 minutes before new logs will appear in SecurityBridgeLogs_CL table.

| | |
|--------------------------|---|
| **Tables Ingested** | `SecurityBridgeLogs_CL` |
| **Connector Definition Files** | [Connector_SecurityBridge.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge%20App/Data%20Connectors/Connector_SecurityBridge.json) |

[→ View full connector details](../connectors/securitybridgesap.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ABAPAuditLog` | [SecurityBridge Solution for SAP](../connectors/securitybridge.md) |
| `SecurityBridgeLogs_CL` | [SecurityBridge Threat Detection for SAP](../connectors/securitybridgesap.md) |

[← Back to Solutions Index](../solutions-index.md)
