# iboss

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | iboss |
| **Support Tier** | Partner |
| **Support Link** | [https://www.iboss.com/contact-us/](https://www.iboss.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2022-02-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] iboss via Legacy Agent](../connectors/iboss.md)

**Publisher:** iboss

### [iboss via AMA](../connectors/ibossama.md)

**Publisher:** iboss

The [iboss](https://www.iboss.com) data connector enables you to seamlessly connect your Threat Console to Microsoft Sentinel and enrich your instance with iboss URL event logs. Our logs are forwarded in Common Event Format (CEF) over Syslog and the configuration required can be completed on the iboss platform without the use of a proxy. Take advantage of our connector to garner critical data points and gain insight into security threats.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure AMA Data Connector**

Steps to configure the iboss AMA Data Connector
**Kindly follow the steps to configure the data connector**

**Step A. Gather Required Configuration Details in Azure Arc**

  1. Navigate to Azure Arc ---> Azure Arc Resources ---> Machines.

2. Add a machine ---> Add a single server ---> Generate script.

3. Select the resource group, this should be the same group as the Log Analytics Workspace for your Microsoft Sentinel instance you will be using

4. Select a region and ensure it is in the same region as your Log Analytics Workspace

5. Select Linux as Operating System

6. Click Next

7. Download the script and use this information for the next step when configuring your Microsoft Sentinel AMA integration iboss side.

8. Navigate to the Log Analytics Workspace of your Microsoft Sentinel instance and find it's resource group, workspace name, and workspace id

  **Step B. Forward Common Event Format (CEF) logs**

  Set your Threat Console to send Syslog messages in CEF format to your Azure workspace. (Ensure you have the information gathered from the previous section)

>1. Navigate to the Integrations Marketplace inside your iboss Console

>2. Select Microsoft Sentinel AMA Log Forwarding

>3. Select Add Integration

4. Use the information from the script and your log analytics workspace to configure the integration.

5. Add the integration

>6. An email with be sent to your iboss alerts email to authenticate. Please do so within five minutes

7. After authenticating, wait 15 to 20 minutes and ensure the Microsoft Sentinel Status of your integration is successful.

  **Step C. Validate connection**

  1. Follow the instructions to validate your connectivity:

2. Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

3. It may take about 20 minutes until the connection streams data to your workspace.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_ibossAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/iboss/Data%20Connectors/template_ibossAMA.json) |

[→ View full connector details](../connectors/ibossama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] iboss via Legacy Agent](../connectors/iboss.md), [iboss via AMA](../connectors/ibossama.md) |

[← Back to Solutions Index](../solutions-index.md)
