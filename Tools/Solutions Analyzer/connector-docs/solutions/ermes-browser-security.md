# Ermes Browser Security

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Ermes Cyber Security S.p.A. |
| **Support Tier** | Partner |
| **Support Link** | [https://www.ermes.company](https://www.ermes.company) |
| **Categories** | domains |
| **First Published** | 2023-09-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ermes%20Browser%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ermes%20Browser%20Security) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Ermes Browser Security Events](../connectors/ermesbrowsersecurityevents.md)

**Publisher:** Ermes Cyber Security S.p.A.

Ermes Browser Security Events

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ErmesBrowserSecurityEvents_CL` |
| **Connector Definition Files** | [ErmesBrowserSecurityEvents_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Ermes%20Browser%20Security/Data%20Connectors/ErmesBrowserSecurityEvents_CCF/ErmesBrowserSecurityEvents_ConnectorDefinition.json) |

[→ View full connector details](../connectors/ermesbrowsersecurityevents.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ErmesBrowserSecurityEvents_CL` | [Ermes Browser Security Events](../connectors/ermesbrowsersecurityevents.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                 |
|-------------|--------------------------------|----------------------------------------------------|
| 3.1.0       | 12-12-2025                     | Added custom API URL support and LogData field with additional event details |
| 3.0.3       | 19-02-2024                     | Updated _solutionVersion to dataConnectorCCPVersion. <br/> Removed grant_type and added the Solution version to the query parameters |
| 3.0.2       | 23-01-2024                     | Updated paging type in **CCP Data Connector**      |
| 3.0.1       | 28-11-2023                     | Updated **CCP Data Connector**                     |
| 3.0.0       | 29-09-2023                     | Initial Solution Release                           |

[← Back to Solutions Index](../solutions-index.md)
