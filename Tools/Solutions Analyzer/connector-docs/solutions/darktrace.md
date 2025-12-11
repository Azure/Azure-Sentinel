# Darktrace

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Darktrace |
| **Support Tier** | Partner |
| **Support Link** | [https://www.darktrace.com/en/contact/](https://www.darktrace.com/en/contact/) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Darktrace](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Darktrace) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Darktrace Connector for Microsoft Sentinel REST API](../connectors/darktracerestconnector.md)

**Publisher:** Darktrace

The Darktrace REST API connector pushes real-time events from Darktrace to Microsoft Sentinel and is designed to be used with the Darktrace Solution for Sentinel. The connector writes logs to a custom log table titled "darktrace_model_alerts_CL"; Model Breaches, AI Analyst Incidents, System Alerts and Email Alerts can be ingested - additional filters can be set up on the Darktrace System Configuration page. Data is pushed to Sentinel from Darktrace masters.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Darktrace Prerequisites**: To use this Data Connector a Darktrace master running v5.2+ is required.
 Data is sent to the [Azure Monitor HTTP Data Collector API](https://docs.microsoft.com/azure/azure-monitor/logs/data-collector-api) over HTTPs from Darktrace masters, therefore outbound connectivity from the Darktrace master to Microsoft Sentinel REST API is required.
- **Filter Darktrace Data**: During configuration it is possible to set up additional filtering on the Darktrace System Configuration page to constrain the amount or types of data sent.
- **Try the Darktrace Sentinel Solution**: You can get the most out of this connector by installing the Darktrace Solution for Microsoft Sentinel. This will provide workbooks to visualise alert data and analytics rules to automatically create alerts and incidents from Darktrace Model Breaches and AI Analyst incidents.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

1. Detailed setup instructions can be found on the Darktrace Customer Portal: https://customerportal.darktrace.com/product-guides/main/microsoft-sentinel-introduction
 2. Take note of the Workspace ID and the Primary key. You will need to enter these details on your Darktrace System Configuration page.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**2. Darktrace Configuration**

1. Perform the following steps on the Darktrace System Configuration page:
 2. Navigate to the System Configuration Page (Main Menu > Admin > System Config)
 3. Go into Modules configuration and click on the "Microsoft Sentinel" configuration card
 4. Select "HTTPS (JSON)" and hit "New"
 5. Fill in the required details and select appropriate filters
 6. Click "Verify Alert Settings" to attempt authentication and send out a test alert
 7. Run a "Look for Test Alerts" sample query to validate that the test alert has been received

| | |
|--------------------------|---|
| **Tables Ingested** | `darktrace_model_alerts_CL` |
| **Connector Definition Files** | [DarktraceConnectorRESTAPI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Darktrace/Data%20Connectors/DarktraceConnectorRESTAPI.json) |

[→ View full connector details](../connectors/darktracerestconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `darktrace_model_alerts_CL` | [Darktrace Connector for Microsoft Sentinel REST API](../connectors/darktracerestconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
