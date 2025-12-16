# MicrosoftDefenderForEndpoint

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft Defender for Endpoint](../connectors/microsoftdefenderadvancedthreatprotection.md)

**Publisher:** Microsoft

Microsoft Defender for Endpoint is a security platform designed to prevent, detect, investigate, and respond to advanced threats. The platform creates alerts when suspicious security events are seen in an organization. Fetch alerts generated in Microsoft Defender for Endpoint to Microsoft Sentinel so that you can effectively analyze security events. You can create rules, build dashboards and author playbooks for immediate response. For more information, see the [Microsoft Sentinel documentation >](https://go.microsoft.com/fwlink/p/?linkid=2220128&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Licenses:**
- Microsoft Defender for Endpoint

**Tenant Permissions:**
Requires GlobalAdmin, SecurityAdmin on the workspace's tenant

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Microsoft Defender for Endpoint alerts to Microsoft Sentinel**

> Connecting Microsoft Defender for Endpoint will cause your data that is collected by Microsoft Defender for Endpoint service to be stored and processed in the location that you have configured your Microsoft Sentinel workspace.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `MicrosoftDefenderATP`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

ℹ️ Microsoft Defender for Endpoint Advanced Hunting raw logs are available as part of the Microsoft 365 Defender (Preview) connector

| | |
|--------------------------|---|
| **Tables Ingested** | `SecurityAlert` |
| **Connector Definition Files** | [template_MicrosoftDefenderAdvancedThreatProtection.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/MicrosoftDefenderForEndpoint/Data%20Connectors/template_MicrosoftDefenderAdvancedThreatProtection.JSON) |

[→ View full connector details](../connectors/microsoftdefenderadvancedthreatprotection.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SecurityAlert` | [Microsoft Defender for Endpoint](../connectors/microsoftdefenderadvancedthreatprotection.md) |

[← Back to Solutions Index](../solutions-index.md)
