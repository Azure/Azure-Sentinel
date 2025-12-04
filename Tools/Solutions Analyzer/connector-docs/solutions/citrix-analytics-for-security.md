# Citrix Analytics for Security

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Citrix Systems |
| **Support Tier** | Partner |
| **Support Link** | [https://www.citrix.com/support/](https://www.citrix.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-05-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20Analytics%20for%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20Analytics%20for%20Security) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [CITRIX SECURITY ANALYTICS](../connectors/citrix.md)

**Publisher:** CITRIX

Citrix Analytics (Security) integration with Microsoft Sentinel helps you to export data analyzed for risky events from Citrix Analytics (Security) into Microsoft Sentinel environment. You can create custom dashboards, analyze data from other sources along with that from Citrix Analytics (Security) and create custom workflows using Logic Apps to monitor and mitigate security events.

| | |
|--------------------------|---|
| **Tables Ingested** | `CitrixAnalytics_indicatorEventDetails_CL` |
| | `CitrixAnalytics_indicatorSummary_CL` |
| | `CitrixAnalytics_riskScoreChange_CL` |
| | `CitrixAnalytics_userProfile_CL` |
| **Connector Definition Files** | [CitrixSecurityAnalytics.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Citrix%20Analytics%20for%20Security/Data%20Connectors/CitrixSecurityAnalytics.json) |

[→ View full connector details](../connectors/citrix.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CitrixAnalytics_indicatorEventDetails_CL` | [CITRIX SECURITY ANALYTICS](../connectors/citrix.md) |
| `CitrixAnalytics_indicatorSummary_CL` | [CITRIX SECURITY ANALYTICS](../connectors/citrix.md) |
| `CitrixAnalytics_riskScoreChange_CL` | [CITRIX SECURITY ANALYTICS](../connectors/citrix.md) |
| `CitrixAnalytics_userProfile_CL` | [CITRIX SECURITY ANALYTICS](../connectors/citrix.md) |

[← Back to Solutions Index](../solutions-index.md)
