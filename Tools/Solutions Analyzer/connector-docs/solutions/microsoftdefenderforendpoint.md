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
