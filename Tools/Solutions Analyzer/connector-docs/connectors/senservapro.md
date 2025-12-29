# SenservaPro (Preview)

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `SenservaPro` |
| **Publisher** | Senserva |
| **Used in Solutions** | [SenservaPro](../solutions/senservapro.md) |
| **Collection Method** | Unknown (Custom Log) |
| **Connector Definition Files** | [SenservaPro.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro/Data%20Connectors/SenservaPro.json) |

The SenservaPro data connector provides a viewing experience for your SenservaPro scanning logs. View dashboards of your data, use queries to hunt & explore, and create custom alerts.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`SenservaPro_CL`](../tables/senservapro-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Setup the data connection**

Visit [Senserva Setup](https://www.senserva.com/senserva-microsoft-sentinel-edition-setup/) for information on setting up the Senserva data connection, support, or any other questions. The Senserva installation will configure a Log Analytics Workspace for output. Deploy Microsoft Sentinel onto the configured Log Analytics Workspace to finish the data connection setup by following [this onboarding guide.](https://docs.microsoft.com/azure/sentinel/quickstart-onboard)
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

## Additional Documentation

> 📄 *Source: [SenservaPro\Data Connectors\SenservaPro_Sentinel_Connector.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SenservaPro\Data Connectors\SenservaPro_Sentinel_Connector.md)*

# Connect your SenservaPro to Azure Sentinel 



The SenservaPro connector allows you to connect SenservaPro Azure Active Directory focused advanced security analytics data with your Azure Sentinel, allowing you view dashboards from Senservaa, create custom alerts, and improve investigation with Hunting queries also provided by Senserva. The Senserva data is multi-tenant enabled. 


> [!NOTE]
>Data is stored in the geographic location of the workspace on which you are running Azure Sentinel.
>Senserva analytics data never leaves the tenant in which Senserva is installed.
>Integration between SenservaPro and Azure Sentinel makes use of the Log Analytics Workspace REST API.

## Configure and connect SenservaPro 

SenservaPro is fully integrated into Azure and exports logs directly to Azure Sentinel every time a Senserva monitored Azure Active Directory configuration changes, or account status changes due to something like a Risky User warning.
1. In the Azure Sentinel portal, click Data connectors and select 'SenservaPro' and then Open connector page.

2. You will install the data provider to the connector as part of your SenservaPro setup from [our Azure Marketplace offering.](https://azuremarketplace.microsoft.com/marketplace/apps/senservallc.senserva)


## Find your data

The data appears in Log Analytics under CustomLogs SenservaPro_CL after a successful connection is established. Senserva data  is continually updated automatically once the connection is established. To use the relevant schema in Log Analytics for the SenservaPro, search for SenservaPro_CL.

## Validate connectivity
It may take up to 20 minutes until your logs start to appear in Log Analytics. 


## Next steps
In this document you learned how to connect SenservaPro to Azure Sentinel. To learn more about Azure Sentinel, see the following articles:
- Learn how to [get visibility into your data, and potential threats](quickstart-get-visibility.md).
- Get started [detecting threats with Azure Sentinel](tutorial-detect-threats-built-in.md).
- [Use workbooks](tutorial-monitor-your-data.md) to monitor your data.

[← Back to Connectors Index](../connectors-index.md)
