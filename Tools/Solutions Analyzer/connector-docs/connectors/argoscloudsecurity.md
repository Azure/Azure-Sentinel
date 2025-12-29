# ARGOS Cloud Security

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `ARGOSCloudSecurity` |
| **Publisher** | ARGOS Cloud Security |
| **Used in Solutions** | [ARGOSCloudSecurity](../solutions/argoscloudsecurity.md) |
| **Collection Method** | Unknown (Custom Log) |
| **Connector Definition Files** | [Connector_ARGOS.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ARGOSCloudSecurity/Data%20Connectors/Connector_ARGOS.json) |

The ARGOS Cloud Security integration for Microsoft Sentinel allows you to have all your important cloud security events in one place. This enables you to easily create dashboards, alerts, and correlate events across multiple systems. Overall this will improve your organization's security posture and security incident response.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`ARGOS_CL`](../tables/argos-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Subscribe to ARGOS**

Ensure you already own an ARGOS Subscription. If not, browse to [ARGOS Cloud Security](https://argos-security.io) and sign up to ARGOS.

Alternatively, you can also purchase ARGOS via the [Azure Marketplace](https://azuremarketplace.microsoft.com/en-au/marketplace/apps/argoscloudsecurity1605618416175.argoscloudsecurity?tab=Overview).

**2. Configure Sentinel integration from ARGOS**

Configure ARGOS to forward any new detections to your Sentinel workspace by providing ARGOS with your Workspace ID and Primary Key.

There is **no need to deploy any custom infrastructure**.

Enter the information into the [ARGOS Sentinel](https://app.argos-security.io/account/sentinel) configuration page.

New detections will automatically be forwarded.

[Learn more about the integration](https://www.argos-security.io/resources#integrations)
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

## Additional Documentation

> 📄 *Source: [ARGOSCloudSecurity\Data Connectors\ARGOS_REST_API_Connector.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ARGOSCloudSecurity\Data Connectors\ARGOS_REST_API_Connector.md)*

# Connect your ARGOS Cloud Security to Azure Sentinel

ARGOS Cloud Security connector allows you to easily connect all your ARGOS Cloud Security security solution logs with your Azure Sentinel, to view dashboards, create custom alerts, and improve investigation. In addition this integration allows you to correlate your ARGOS Cloud Security events to other events that are happening in your environment. Integration between ARGOS Cloud Security and Azure Sentinel makes use of REST API.

> [!NOTE]
> Data will be stored in the geographic location of the workspace on which you are running Azure Sentinel. This can be different to the geographic location of your ARGOS Cloud Security subscription.

## Configure and connect ARGOS Cloud Security

ARGOS Cloud Security can integrate and export detections directly to Azure Sentinel.

1. In the Azure Sentinel portal, click Data connectors and select ARGOS Cloud Security and then Open connector page.
2. Either follow the instructions on the [ARGOS Resources](https://www.argos-security.io/resources#integrations) page on how to configure the integration or if you are already logged in to ARGOS then head to the [Sentinel integration page](https://app.argos-security.io/account/sentinel) and configure it right away.

## Find your data

After a successful connection is established, the data appears in Log Analytics under CustomLogs ARGOS_CL.
To use the relevant schema in Log Analytics for the ARGOS Cloud Security, search for ARGOS_CL.

## Validate connectivity

It may take up to 20 minutes until your logs start to appear in Log Analytics.

## Next steps

In this document, you learned how to connect ARGOS Cloud Security to Azure Sentinel.

[← Back to Connectors Index](../connectors-index.md)
