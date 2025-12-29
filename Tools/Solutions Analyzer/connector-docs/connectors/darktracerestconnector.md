# Darktrace Connector for Microsoft Sentinel REST API

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `DarktraceRESTConnector` |
| **Publisher** | Darktrace |
| **Used in Solutions** | [Darktrace](../solutions/darktrace.md) |
| **Collection Method** | REST API |
| **Connector Definition Files** | [DarktraceConnectorRESTAPI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Darktrace/Data%20Connectors/DarktraceConnectorRESTAPI.json) |

The Darktrace REST API connector pushes real-time events from Darktrace to Microsoft Sentinel and is designed to be used with the Darktrace Solution for Sentinel. The connector writes logs to a custom log table titled "darktrace_model_alerts_CL"; Model Breaches, AI Analyst Incidents, System Alerts and Email Alerts can be ingested - additional filters can be set up on the Darktrace System Configuration page. Data is pushed to Sentinel from Darktrace masters.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`darktrace_model_alerts_CL`](../tables/darktrace-model-alerts-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Darktrace Prerequisites**: To use this Data Connector a Darktrace master running v5.2+ is required.
 Data is sent to the [Azure Monitor HTTP Data Collector API](https://docs.microsoft.com/azure/azure-monitor/logs/data-collector-api) over HTTPs from Darktrace masters, therefore outbound connectivity from the Darktrace master to Microsoft Sentinel REST API is required.
- **Filter Darktrace Data**: During configuration it is possible to set up additional filtering on the Darktrace System Configuration page to constrain the amount or types of data sent.
- **Try the Darktrace Sentinel Solution**: You can get the most out of this connector by installing the Darktrace Solution for Microsoft Sentinel. This will provide workbooks to visualise alert data and analytics rules to automatically create alerts and incidents from Darktrace Model Breaches and AI Analyst incidents.

## Setup Instructions

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

## Additional Documentation

> 📄 *Source: [Darktrace\Data Connectors\Doc_DarktraceConnectorRESTAPI.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Darktrace\Data Connectors\Doc_DarktraceConnectorRESTAPI.md)*

<!-- Taken from https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/Templates/Doc_Template_REST_API_Connector.md -->

# Connect Darktrace to Microsoft Sentinel 


The Darktrace Data Connector allows you to easily connect your AI detections from within Darktrace's Product Suite with your Microsoft Sentinel workspace, to view dashboards, create custom alerts, and improve investigation. The connector allows Darktrace to send AI Analyst Incidents, Model Breaches, Email Alerts and System Health Alerts to Sentinel. Integration between Darktrace and Microsoft Sentinel makes use of REST API: data is sent from Darktrace to Sentinel using HTTPs.


> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Microsoft Sentinel.

## Configure and connect Darktrace to Microsoft Sentinel

Darktrace can integrate and export alerting data directly to Microsoft Sentinel.

1. In the Microsoft Sentinel portal, click Data connectors and select "Darktrace Connector for Microsoft Sentinel REST API" and then Open connector page.

2. Follow the configuration steps in the configuration wizard. Detailed configuration steps can be found on the [Darktrace Customer Portal](https://customerportal.darktrace.com/product-guides/main/microsoft-sentinel-introduction).

## Find your data

After a successful connection is established, the data appears in Log Analytics under CustomLogs `darktrace_model_alerts_CL`.
To use the relevant schema in Log Analytics for Darktrace, search for `darktrace_model_alerts_CL`.

## Validate connectivity
It may take up to 20 minutes until your logs start to appear in Log Analytics. You can look for test alerts sent during connection validation by using one of the sample queries shipping with the connector.


## Next steps
In this document, you learned how to connect Darktrace to Microsoft Sentinel. To learn more about Microsoft Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](https://docs.microsoft.com/azure/sentinel/get-visibility).
- Get started [detecting threats with Microsoft Sentinel](https://docs.microsoft.com/azure/sentinel/detect-threats-built-in).
- [Use workbooks](https://docs.microsoft.com/azure/sentinel/monitor-your-data) to monitor your data.

### Install as a solution (Preview)

To get the most out of the Data Connector, consider installing the Darktrace Solution for Microsoft Sentinel from the Sentinel Content Hub. The solution will allow you to operationalize Darktrace data in Microsoft Sentinel by visualising alerting using Workbooks as well as turning Darktrace alerting into Microsoft Sentinel Incident and Alerts.

For more information, see the [Microsoft Sentinel solution overview](https://docs.microsoft.com/azure/sentinel/sentinel-solutions) and visit the [Azure Marketplace](https://azure.microsoft.com/marketplace/)

[← Back to Connectors Index](../connectors-index.md)
