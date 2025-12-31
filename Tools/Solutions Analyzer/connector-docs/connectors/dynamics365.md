# Dynamics 365

| Attribute | Value |
|:----------|:------|
| **Connector ID** | `Dynamics365` |
| **Publisher** | Microsoft |
| **Used in Solutions** | [Dynamics 365](../solutions/dynamics-365.md) |
| **Collection Method** | Native |
| **Connector Definition Files** | [template_Dynamics365.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynamics%20365/Data%20Connectors/template_Dynamics365.json) |

The Dynamics 365 Common Data Service (CDS) activities connector provides insight into admin, user, and support activities, as well as Microsoft Social Engagement logging events. By connecting Dynamics 365 CRM logs into Microsoft Sentinel, you can view this data in workbooks, use it to create custom alerts, and improve your investigation process. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com//fwlink/p/?linkid=2226719&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`Dynamics365Activity`](../tables/dynamics365activity.md) | ✓ | ✗ |

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **Tenant Permissions**: 'Security Administrator' or 'Global Administrator' on the workspace's tenant.
- **License**: [Microsoft Dynamics 365 production license](https://docs.microsoft.com/office365/servicedescriptions/microsoft-dynamics-365-online-service-description) (This connector is available for production environments only, not for sandbox). Also, a Microsoft 365 Enterprise [E3 or E5](https://docs.microsoft.com/power-platform/admin/enable-use-comprehensive-auditing#requirements) subscription is required for Activity Logging.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

Connect [Dynamics 365 CRM](https://aka.ms/Sentinel/Dynamics365) activity logs to your Microsoft Sentinel workspace.
- Connect Dynamics365

[← Back to Connectors Index](../connectors-index.md)
