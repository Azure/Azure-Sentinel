# Forescout Host Property Monitor

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `ForescoutHostPropertyMonitor` |
| **Publisher** | Forescout |
| **Used in Solutions** | [ForescoutHostPropertyMonitor](../solutions/forescouthostpropertymonitor.md) |
| **Collection Method** | Unknown (Custom Log) |
| **Connector Definition Files** | [ForescoutHostPropertyMonitor.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ForescoutHostPropertyMonitor/Data%20Connectors/ForescoutHostPropertyMonitor.json) |

The Forescout Host Property Monitor connector allows you to connect host/policy/compliance properties from Forescout platform with Microsoft Sentinel, to view, create custom incidents, and improve investigation. This gives you more insight into your organization network and improves your security operation capabilities.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`ForescoutComplianceStatus_CL`](../tables/forescoutcompliancestatus-cl.md) | — | — |
| [`ForescoutHostProperties_CL`](../tables/forescouthostproperties-cl.md) | — | — |
| [`ForescoutPolicyStatus_CL`](../tables/forescoutpolicystatus-cl.md) | — | — |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Forescout Plugin requirement**: Please make sure Forescout Microsoft Sentinel plugin is running on Forescout platform

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Instructions on how to configure Forescout Microsoft Sentinel plugin are provided at Forescout Documentation Portal (https://docs.forescout.com/bundle/microsoft-sentinel-module-v2-0-0-h)
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
